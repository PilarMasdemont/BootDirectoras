import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI

# Función real que explica la página 2 del informe
from funciones.explicar_ratio_diario import explicar_ratio_diario

# Cargar clave de API
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY no está configurado.")

client = OpenAI(api_key=API_KEY)

# Registrar funciones disponibles para el asistente
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

# Crear la aplicación FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, reemplaza con el dominio real del frontend
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
        "para la directora del salón en español claro y directo."
    )

    # Primera llamada al asistente
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

    # Si llama a una función
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

    # Si responde directamente sin función
    return {"respuesta": msg.content}
