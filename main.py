import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd

# Función real que explica la página 2 del informe
from funciones.explicar_ratio_diario import explicar_ratio_diario
# Función real que explica la página 3 del informe
from funciones.explicar_ratio_semanal import explicar_ratio_semanal


# Cargar clave de API
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY no está configurado.")

client = OpenAI(api_key=API_KEY)

# Definición de la función para el LLM
default_schema = [
    {
        "name": "explicar_ratio_diario",
        "description": "Explica por qué el Ratio General fue alto, medio o bajo en un día concreto para un salón, basándose en otros KPIs diarios.",
        "parameters": {
            "type": "object",
            "properties": {
                "codsalon": {"type": "string", "description": "Código único del salón que aparece en los datos de Google Sheets"},
                "fecha": {"type": "string", "description": "Fecha en formato 'YYYY-MM-DD' correspondiente al día que se quiere analizar"}
            },
            "required": ["codsalon", "fecha"]
        }
    }
]

{
    "name": "explicar_ratio_semanal",
    "description": "Explica por qué el Ratio General fue alto, medio o bajo en una semana concreta para un salón, basándose en otros KPIs semanales.",
    "parameters": {
        "type": "object",
        "properties": {
            "codsalon": {"type": "string", "description": "Código del salón"},
            "nsemana": {"type": "integer", "description": "Número de semana del año (1-52)"},
            "year": {"type": "integer", "description": "Año en formato YYYY"}
        },
        "required": ["codsalon", "nsemana", "year"]
    }
}


# Crear la aplicación FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajustar en producción
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

    if not mensaje_usuario or not codsalon or not fecha:
        raise HTTPException(400, "Faltan campos obligatorios: 'mensaje', 'codsalon' o 'fecha'.")

    # Inyectar contexto en el mensaje para guiar al LLM
    mensaje = f"[codsalon={codsalon}]\n[fecha={fecha}]\n{mensaje_usuario}"

    # Prompt del sistema reforzado para llamadas a función\  
    system_prompt = (
        "Actúa como Mont Dirección. Siempre comienza tus respuestas saludando, por ejemplo: 'Hola, soy Mont Dirección.'\n\n"
        "Eres una asistente experta en KPIs de salones de peluquería.\n\n"
        "Cuando el usuario haga una pregunta sobre un KPI en un día concreto, deberás invocar la función `explicar_ratio_diario`"
        " con los parámetros: { \"codsalon\": <valor>, \"fecha\": \"YYYY-MM-DD\" }.\n\n"
        "Estos valores siempre vendrán inyectados en el mensaje del usuario con etiquetas como:\n"
        "[codsalon=1]\n[fecha=2025-04-26]\n\n"
        "Tras recibir el resultado de la función, responde con una explicación clara en español, en tono profesional pero accesible."
    )

    # Primera llamada al LLM
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": mensaje}
        ],
        functions=default_schema,
        function_call="auto"
    )

    mensaje_llm = response.choices[0].message

    # Si el modelo invocó la función
    if mensaje_llm.function_call:
        func_name = mensaje_llm.function_call.name
        func_args = json.loads(mensaje_llm.function_call.arguments)
        try:
            result = globals()[func_name](**func_args)
        except Exception as e:
            result = f"⚠️ Error al ejecutar la función {func_name}: {str(e)}"

        # Llamada de seguimiento para generar respuesta final\  
        follow = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mensaje},
                {"role": "function", "name": func_name, "content": result}
            ]
        )
        return {"respuesta": follow.choices[0].message.content}

    # Fallback: invocar la función directamente
    fallback = explicar_ratio_diario(codsalon, fecha)
    return {"respuesta": f"Hola, soy Mont Dirección.\n\n{fallback}"}

# Nuevo endpoint: /kpis/30dias
from sheets import cargar_hoja

# Endpoint adicional para KPIs diarios (Hoja 2)
@app.get("/kpis/30dias")
def get_kpis_30dias(codsalon: str):
    try:
        df = cargar_hoja("1882861530")  # GID real de la hoja KPIs_30Dias
        datos_filtrados = df[df['codsalon'].astype(str) == codsalon]
        return datos_filtrados.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from funciones.explicar_ratio_diario import router as debug_router
app.include_router(debug_router)

# Endpoint adicional para KPIs semanales (Hoja 3)
@app.get("/kpis/semanal")
def get_kpis_semanales(codsalon: str):
    try:
        df = cargar_hoja("72617950")  # GID de la hoja de KPIs semanales
        datos_filtrados = df[df['codsalon'].astype(str) == codsalon]
        return datos_filtrados.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
