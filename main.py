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

    if not mensaje:
        raise HTTPException(status_code=400, detail="Mensaje no proporcionado")

    system_prompt = """
    Eres Mont Dirección, un asistente experto en análisis de salones de belleza.
    Ayudas a interpretar ratios de productividad, tiempo indirecto, y tickets medios, basándote en datos diarios y semanales.
    Tus respuestas son claras, concisas y con recomendaciones si detectas problemas.
    """.strip()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Primera llamada al LLM
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": mensaje}
        ]
    )

    mensaje_llm = response.choices[0].message
    content = mensaje_llm.content or ""

    # Lógica alternativa si queremos invocar funciones manualmente
    if "ratio diario" in mensaje.lower():
        codsalon = body.get("codsalon")
        fecha = body.get("fecha")
        if not codsalon or not fecha:
            return {"respuesta": content}
        resultado = explicar_ratio_diario(codsalon, fecha)
        return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}

    if "ratio semanal" in mensaje.lower():
        codsalon = body.get("codsalon")
        nsemana = body.get("nsemana")
        year = body.get("year")
        if not codsalon or not nsemana or not year:
            return {"respuesta": content}
        resultado = explicar_ratio_semanal(codsalon, int(nsemana), int(year))
        return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}

    return {"respuesta": content}
