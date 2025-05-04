import os
import json
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI

# Funciones propias
from funciones.kpis import consultar_kpis
from funciones.analizar_salon import analizar_salon
from funciones.analizar_trabajadores import analizar_trabajadores
from funciones.explicar_kpi import explicar_kpi
from funciones.explicar_variacion import explicar_variacion
from funciones.sugerencias_mejora import sugerencias_mejora

# Carga claves
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY no está configurado.")

client = OpenAI(api_key=API_KEY)

# Funciones expuestas a GPT
function_schema = [
    {
        "name": fn.__name__,
        "description": fn.__doc__ or fn.__name__,
        "parameters": {
            "type": "object",
            "properties": {
                "year": {"type": "integer"},
                "nsemana": {"type": "integer"},
                "codsalon": {"type": "integer"},
                "tipo": {
                    "type": "string",
                    "enum": ["semana", "trabajadores", "mensual", "mensual_comparado"]
                }
            },
            "required": ["year", "nsemana", "codsalon"]
        }
    } for fn in [
        consultar_kpis,
        analizar_salon,
        analizar_trabajadores,
        explicar_kpi,
        explicar_variacion,
        sugerencias_mejora
    ]
]

# App FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar por el dominio del frontend en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat_handler(request: Request):
    data = await request.json()
    mensaje = data.get("mensaje")
    if not mensaje:
        raise HTTPException(400, "Falta el campo 'mensaje'.")

    system_prompt = (
        "Actúa como Mont Dirección. "
        "Contesta siempre con un saludo, y presentándote: Soy Mont Dirección.\n\n"
        "Eres un asistente especializado en ayudar a directoras de salones de peluquería. "
        "Tu función es ayudarles a entender cómo mejorar su negocio.\n\n"
        "Después de llamar a una función y recibir su respuesta, escribe siempre una respuesta explicativa "
        "para la directora del salón en español claro y directo.\n\n"
        "⚠️ Usa los nombres de los parámetros exactamente como están definidos en las funciones: year, nsemana, codsalon, tipo.\n\n"
        "🗓️ Siempre asume que el año actual es 2025, salvo que la directora indique explícitamente otro año. "
        "Interpreta correctamente expresiones como 'esta semana', 'el mes pasado', o 'la semana 14'."
    )

    # Primera llamada
    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": mensaje}
        ],
        functions=function_schema,
        function_call="auto"
    )

    msg = res.choices[0].message

    # Si llama a función
    if msg.function_call:
        nombre = msg.function_call.name
        args = json.loads(msg.function_call.arguments)

        try:
            resultado = globals()[nombre](**args)
        except Exception as e:
            resultado = f"⚠️ Error al ejecutar la función {nombre}: {str(e)}"

        follow = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mensaje},
                {
                    "role": "function",
                    "name": nombre,
                    "content": resultado
                }
            ]
        )
        return {"respuesta": follow.choices[0].message.content}

    # Si no llama función
    return {"respuesta": msg.content}
