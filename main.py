import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd

# --- CONFIGURACIÓN ---
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY no está configurado.")

GID_KPIS_30DIAS = 1882861530  # GID hoja KPIs_30Dias
from sheets import cargar_hoja
from funciones.explicar_ratio_diario import explicar_ratio_diario

client = OpenAI(api_key=API_KEY)

function_schema = [
    {
        "name": "explicar_ratio_diario",
        "description": "Explica por qué el Ratio General fue alto, medio o bajo en un día concreto para un salón, basándose en otros KPIs diarios.",
        "parameters": {
            "type": "object",
            "properties": {
                "codsalon": {"type": "string"},
                "fecha":    {"type": "string"}
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

# --- ENDPOINT /chat ---
@app.post("/chat")
async def chat_handler(request: Request):
    data = await request.json()
    mensaje_usuario = data.get("mensaje")
    codsalon       = data.get("codsalon")
    fecha          = data.get("fecha")

    if not mensaje_usuario or not codsalon or not fecha:
        raise HTTPException(400, "Faltan campos obligatorios: mensaje, codsalon o fecha.")

    # Inyectar tags para guiar la llamada a función
    mensaje = (
        f"[codsalon={codsalon}]\n"
        f"[fecha={fecha}]\n"
        f"{mensaje_usuario}"
    )

    system_prompt = (
        "Actúa como Mont Dirección. Siempre comienza saludando: 'Hola, soy Mont Dirección.'\n\n"
        "Eres una asistente experta en KPIs de salones de peluquería.\n\n"
        "Cuando el usuario pregunte por un KPI en un día concreto, "
        "debes invocar la función `explicar_ratio_diario` con parámetros "
        "{ 'codsalon': <valor>, 'fecha': 'YYYY-MM-DD' }.\n\n"
        "Estos valores siempre vendrán inyectados en el mensaje como:\n"
        "[codsalon=1]\n[fecha=2025-04-26]\n\n"
        "Después de ejecutar la función, responde con una explicación clara en español."
    )

    # Primera pasada: forzar function calling
    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": mensaje}
        ],
        functions=function_schema,
        function_call="auto"
    )
    msg = res.choices[0].message

    # Si GPT decide llamar a la función...
    if msg.function_call:
        args = json.loads(msg.function_call.arguments)
        try:
            resultado = explicar_ratio_diario(**args)
        except Exception as e:
            resultado = f"⚠️ Error al ejecutar la función: {e}"

        # Segunda pasada: GPT envuelve la salida de la función
        follow = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system",  "content": system_prompt},
                {"role": "user",    "content": mensaje},
                {"role": "function","name": msg.function_call.name, "content": resultado}
            ]
        )
        return {"respuesta": follow.choices[0].message.content}

    # Fallback (no se invocó la función)
    return {"respuesta": msg.content}


# --- ENDPOINT /kpis/30dias ---
@app.get("/kpis/30dias")
async def get_kpis_30dias(codsalon: int):
    """
    Devuelve los registros de los últimos 30 días para el salón indicado.
    Parámetro: codsalon (int)
    """
    try:
        df = cargar_hoja(GID_KPIS_30DIAS)
    except Exception as e:
        raise HTTPException(500, f"Error cargando datos desde Google Sheets: {e}")

    # Asegurarse de que la columna existe y filtrar
    if 'codsalon' not in df.columns:
        raise HTTPException(500, "La hoja no contiene la columna 'codsalon'.")

    # Normalizar tipos y filtrar
    df['codsalon'] = pd.to_numeric(df['codsalon'], errors="coerce")
    filtrado = df[df['codsalon'] == codsalon]

    # Convertir a JSON
    records = filtrado.to_dict(orient="records")
    return {"codsalon": codsalon, "datos": records}

