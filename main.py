import httpx
import pandas as pd
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
import os
from funciones.explicar_ratio_diario import explicar_ratio_diario
from funciones.explicar_ratio_semanal import explicar_ratio_semanal
from sheets import cargar_hoja

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

# Endpoint: KPIs diarios (últimos 30 días)
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

# Endpoint: Columnas disponibles (debug)
@app.get("/debug/columnas")
def columnas_disponibles():
    try:
        df = cargar_hoja("1882861530")
        return {"columnas": list(df.columns)}
    except Exception as e:
        return {"error": str(e)}

# Endpoint principal para conversación
@app.post("/chat")
async def chat_handler(request: Request):
    body = await request.json()
    mensaje = body.get("mensaje", "")
    codsalon = body.get("codsalon")
    fecha = body.get("fecha")
    nsemana = body.get("nsemana")

    if not mensaje:
        raise HTTPException(status_code=400, detail="Mensaje no proporcionado")

    system_prompt = """
    Eres Mont Dirección, un asistente experto en análisis de salones de belleza.
    Trabajas exclusivamente con datos del año 2025.
    Ayudas a interpretar ratios de productividad, tiempo indirecto y tickets medios, basándote en datos diarios o semanales.
    Si necesitas datos adicionales pregunta a la directora antes de responder.
    """.strip()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Llamada al modelo con funciones definidas
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": mensaje}
        ],
        function_call="auto",
        functions=[
            {
                "name": "explicar_ratio_diario",
                "description": "Explica por qué el ratio fue alto en un día concreto de un salón.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "codsalon": {"type": "string"},
                        "fecha": {"type": "string", "description": "Formato: YYYY-MM-DD"}
                    },
                    "required": ["codsalon", "fecha"]
                }
            },
            {
                "name": "explicar_ratio_semanal",
                "description": "Explica por qué el ratio fue alto en una semana concreta de un salón.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "codsalon": {"type": "string"},
                        "nsemana": {"type": "integer", "description": "Número de semana del año (1 a 53)"}
                    },
                    "required": ["codsalon", "nsemana"]
                }
            }
        ]
    )

    message = response.choices[0].message

    if message.function_call:
        fn_name = message.function_call.name
        arguments = json.loads(message.function_call.arguments)

        if fn_name == "explicar_ratio_diario":
            resultado = explicar_ratio_diario(
                arguments.get("codsalon"), arguments.get("fecha")
            )
            return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}

        elif fn_name == "explicar_ratio_semanal":
            resultado = explicar_ratio_semanal(
                arguments.get("codsalon"), arguments.get("nsemana"), 2025
            )
            return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}

    return {"respuesta": message.content or "No se pudo generar una respuesta."}

