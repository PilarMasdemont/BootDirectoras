
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
    fecha = data.get("fecha")

    if not codsalon or not fecha:
        raise HTTPException(400, "Faltan los campos 'codsalon' o 'fecha'.")

    mensaje = f"[codsalon={codsalon}]
[fecha={fecha}]
{mensaje_usuario}"

    system_prompt = (
        "Actúa como Mont Dirección. Siempre comienza tus respuestas saludando, por ejemplo: 'Hola, soy Mont Dirección.'\n\n"
        "Eres una asistente experta en KPIs de salones de peluquería.\n\n"
        "Cuando el usuario haga una pregunta sobre un KPI en un día concreto, deberás invocar la función "
        "`explicar_ratio_diario` con los parámetros:\n"
        '{ "codsalon": <valor>, "fecha": "YYYY-MM-DD" }\n\n'
        "Estos valores siempre vendrán inyectados en el mensaje del usuario con etiquetas como:\n"
        "[codsalon=1]\n[fecha=2025-04-26]\n\n"
        "Después de recibir el resultado de la función, responde con una explicación clara en español, en tono profesional pero accesible."
    )

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
                {"role": "function", "name": nombre, "content": resultado}
            ]
        )
        return {"respuesta": follow.choices[0].message.content}

    # Fallback: ejecuta tú mismo si el modelo no llamó a la función
    resultado = explicar_ratio_diario(codsalon, fecha)
    return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}

