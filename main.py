import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI

from funciones.explicar_ratio_diario import explicar_ratio_diario

# Cargar clave de API
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY no está configurado.")

client = OpenAI(api_key=API_KEY)

function_schema = [
    {
        "name": "explicar_ratio_diario",
        "description": "Explica por qué el Ratio General fue alto, medio o bajo en un día concreto para un salón, basándose en otros KPIs diarios.",
        "parameters": {
            "type": "object",
            "properties": {
                "codsalon": {
                    "type": "string",
                    "description": "Código único del salón que aparece en los datos de Google Sheets"
                },
                "fecha": {
                    "type": "string",
                    "description": "Fecha en formato 'YYYY-MM-DD' correspondiente al día que se quiere analizar"
                }
            },
            "required": ["codsalon", "fecha"]
        }
    }
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat_handler(request: Request):
    data = await request.json()
    mensaje_usuario = data.get("mensaje")
    codsalon = data.get("codsalon")

    if not mensaje_usuario:
        raise HTTPException(400, "Falta el campo 'mensaje'.")
    if not codsalon:
        raise HTTPException(400, "Falta el campo 'codsalon'.")

    # Inyectar el codsalon como contexto implícito en el mensaje
    mensaje = (
        f"[codsalon={codsalon}]\n"
        f"{mensaje_usuario}"
    )

    system_prompt = (
        "Actúa como Mont Dirección.\n"
        "Contesta siempre con un saludo, y presentándote: Soy Mont Dirección.\n\n"
        "Eres un asistente especializado en ayudar a directoras de salones de peluquería. "
        "Tu función es ayudarles a entender cómo mejorar su negocio.\n\n"
        "Si ves un mensaje como [codsalon=1], significa que debes usar ese código de salón aunque la directora no lo mencione en su mensaje.\n"
        "Después de llamar a una función y recibir su respuesta, escribe siempre una respuesta explicativa "
        "para la directora del salón en español claro y directo."
    )

    # Llamada inicial al modelo
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

    return {"respuesta": msg.content}

