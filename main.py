import httpx
import pandas as pd
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from openai.types.chat import FunctionDefinition
from dotenv import load_dotenv
import os
from funciones.explicar_ratio_diario import explicar_ratio_diario
from funciones.explicar_ratio_semanal import explicar_ratio_semanal
from sheets import cargar_hoja
import json

load_dotenv()

app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint: KPIs diarios (ultimos 30 dias)
@app.get("/kpis/30dias")
def get_kpis_diarios(codsalon: str):
    try:
        df = cargar_hoja("1882861530")
        datos_filtrados = df[df['codsalon'].astype(str) == codsalon]
        return datos_filtrados.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint: KPIs semanales
@app.get("/kpis/semanal")
def get_kpis_semanales(codsalon: str):
    try:
        df = cargar_hoja("72617950")
        datos_filtrados = df[df['codsalon'].astype(str) == codsalon]
        return datos_filtrados.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint: columnas disponibles (debug)
@app.get("/debug/columnas")
def columnas_disponibles():
    try:
        df = cargar_hoja("1882861530")
        return {"columnas": list(df.columns)}
    except Exception as e:
        return {"error": str(e)}

# Definicion de funciones para LLM
function_llm_spec = [
    FunctionDefinition(
        name="explicar_ratio_diario",
        description="Explica por que el ratio fue alto en un dia concreto de un salon.",
        parameters={
            "type": "object",
            "properties": {
                "codsalon": {"type": "string"},
                "fecha": {"type": "string", "description": "Formato: YYYY-MM-DD"},
            },
            "required": ["codsalon", "fecha"]
        }
    ),
    FunctionDefinition(
        name="explicar_ratio_semanal",
        description="Explica por que el ratio fue alto en una semana concreta de un salon.",
        parameters={
            "type": "object",
            "properties": {
                "codsalon": {"type": "string"},
                "nsemana": {"type": "integer", "description": "Numero de semana del ano (1 a 53)"},
                "year": {"type": "integer", "description": "Ano, por ejemplo 2025"},
            },
            "required": ["codsalon", "nsemana", "year"]
        }
    )
]

# Chat principal
@app.post("/chat")
async def chat_handler(request: Request):
    body = await request.json()
    mensaje = body.get("mensaje", "")
    codsalon = body.get("codsalon")
    fecha = body.get("fecha")
    nsemana = body.get("nsemana")
    year = body.get("year")

    if not mensaje:
        raise HTTPException(status_code=400, detail="Mensaje no proporcionado")

    system_prompt = """
    Eres Mont Direccion, un asistente experto en analisis de salones de belleza.
    Ayudas a interpretar ratios de productividad, tiempo indirecto y tickets medios, basandote en datos diarios o semanales.
    Si necesitas datos adicionales pregunta a la directora antes de responder.
    """.strip()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": mensaje}
        ],
        functions=function_llm_spec,
        function_call="auto"
    )

    message = response.choices[0].message

    if message.function_call:
        fn_name = message.function_call.name
        arguments = json.loads(message.function_call.arguments)

        if fn_name == "explicar_ratio_diario":
            resultado = explicar_ratio_diario(
                arguments.get("codsalon"), arguments.get("fecha")
            )
            return {"respuesta": f"Hola, soy Mont Direccion.\n\n{resultado}"}

        elif fn_name == "explicar_ratio_semanal":
            resultado = explicar_ratio_semanal(
                arguments.get("codsalon"), arguments.get("nsemana"), arguments.get("year")
            )
            return {"respuesta": f"Hola, soy Mont Direccion.\n\n{resultado}"}

    return {"respuesta": message.content or "No se pudo generar una respuesta."}
