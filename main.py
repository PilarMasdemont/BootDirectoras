import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI

# Importar tu función real
from funciones.explicar_ratio_diario import explicar_ratio_diario

# Carga de la clave de API
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY no está configurado.")

client = OpenAI(api_key=API_KEY)

# Definición del schema de funciones para OpenAI
function_schema = [
    {
        "name": "explicar_ratio_diario",
        "description": (
            "Explica por qué el Ratio General fue alto, medio o bajo en un día concreto "
            "para un salón, basándose en otros KPIs diarios."
        ),
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
    allow_origins=["*"],  # En producción, restringe al dominio de la intranet
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

    # Validar que recibimos todo lo necesario
    if not mensaje_usuario or not codsalon or not fecha:
        raise HTTPException(
            400,
            "Faltan campos en la petición. "
            "Asegúrate de enviar 'mensaje', 'codsalon' y 'fecha' en ISO (YYYY-MM-DD)."
        )

    # Inyectar tags para forzar la llamada a la función
    prompt_user = (
        f"[codsalon={codsalon}]\n"
        f"[fecha={fecha}]\n"
        f"{mensaje_usuario}"
    )

    system_prompt = (
        "Actúa como Mont Dirección. "
        "Contesta siempre con un saludo presentándote: Soy Mont Dirección.\n\n"
        "Eres un asistente especializado en ayudar a directoras de salones de peluquería. "
        "Tu función es ayudarles a entender cómo mejorar su negocio.\n\n"
        "— Si el usuario pregunta por un KPI en un día concreto, debes invocar la función "
        "`explicar_ratio_diario` con los parámetros "
        '`{"codsalon": <valor>, "fecha": "<YYYY-MM-DD>"}´. '
        "Solo después de recibir el resultado de la función, genera tu respuesta explicativa."
    )

    # Primera llamada al modelo
    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": prompt_user}
        ],
        functions=function_schema,
        function_call="auto"
    )

    msg = res.choices[0].message

    # Si el modelo ha decidido llamar a tu función:
    if msg.function_call:
        fn_name = msg.function_call.name
        fn_args = json.loads(msg.function_call.arguments)
        try:
            fn_result = globals()[fn_name](**fn_args)
        except Exception as e:
            fn_result = f"⚠️ Error interno al ejecutar la función: {e}"

        # Segunda llamada para que GPT mezcle el resultado en texto
        follow = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system",   "content": system_prompt},
                {"role": "user",     "content": prompt_user},
                {"role": "function", "name": fn_name, "content": fn_result}
            ]
        )
        return {"respuesta": follow.choices[0].message.content}

    # **Fallback**: si GPT no invocó la función, la llamamos directamente
    resultado_directo = explicar_ratio_diario(codsalon, fecha)
    respuesta = f"¡Hola! Soy Mont Dirección.\n\n{resultado_directo}"
    return {"respuesta": respuesta}

