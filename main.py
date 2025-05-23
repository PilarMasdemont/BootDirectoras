import httpx
import pandas as pd
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from funciones.explicar_ratio_diario import explicar_ratio_diario
from funciones.explicar_ratio_semanal import explicar_ratio_semanal
from funciones.explicar_ratio_mensual import explicar_ratio_mensual
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

# Endpoints de KPIs y debugging
@app.get("/kpis/30dias")
def get_kpis_diarios(codsalon: str):
    try:
        df = cargar_hoja("1882861530")
        datos_filtrados = df[df['codsalon'].astype(str) == codsalon]
        return datos_filtrados.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpis/semanal")
def get_kpis_semanales(codsalon: str):
    try:
        df = cargar_hoja("72617950")
        datos_filtrados = df[df['codsalon'].astype(str) == codsalon]
        return datos_filtrados.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Definiciones de funciones para el modelo
function_llm_spec = [
    {
        "name": "explicar_ratio_diario",
        "description": "Explica el valor del Ratio General en un día concreto.",
        "parameters": {
            "type": "object",
            "properties": {
                "codsalon": {"type": "string"},
                "fecha": {"type": "string", "description": "Formato: YYYY-MM-DD"},
            },
            "required": ["codsalon", "fecha"]
        },
    },
    {
        "name": "explicar_ratio_semanal",
        "description": "Explica el valor del Ratio General semanal de un salón.",
        "parameters": {
            "type": "object",
            "properties": {
                "codsalon": {"type": "string"},
                "nsemana": {"type": "integer"},
            },
            "required": ["codsalon", "nsemana"]
        },
    },
    {
        "name": "explicar_ratio_mensual",
        "description": "Explica el Ratio General mensual por empleado en un salón.",
        "parameters": {
            "type": "object",
            "properties": {
                "codsalon": {"type": "string"},
                "mes": {"type": "integer"},
                "codempleado": {"type": "string"},
            },
            "required": ["codsalon", "mes", "codempleado"]
        },
    },
]

# Chat principal
@app.post("/chat")
async def chat_handler(request: Request):
    body = await request.json()
    mensaje = body.get("mensaje", "")
    codsalon = body.get("codsalon")
    fecha = body.get("fecha")
    nsemana = body.get("nsemana")
    mes = body.get("mes")
    codempleado = body.get("codempleado")

    if not mensaje:
        raise HTTPException(status_code=400, detail="Mensaje no proporcionado")

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": mensaje}
            ],
            functions=function_llm_spec,
            function_call="auto",
        )

        msg = response.choices[0].message

        if msg.function_call:
            nombre_funcion = msg.function_call.name
            argumentos = json.loads(msg.function_call.arguments)

            if nombre_funcion == "explicar_ratio_diario":
                resultado = explicar_ratio_diario(**argumentos)
            elif nombre_funcion == "explicar_ratio_semanal":
                resultado = explicar_ratio_semanal(**argumentos)
            elif nombre_funcion == "explicar_ratio_mensual":
                resultado = explicar_ratio_mensual(**argumentos)
            else:
                raise HTTPException(status_code=400, detail="Función no reconocida")

            return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}

        return {"respuesta": msg.content or "No se recibió contenido del asistente."}

    except Exception as e:
        return {"error": str(e)}
