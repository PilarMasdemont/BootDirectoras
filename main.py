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

print("🗂 Directorio actual:", os.getcwd())
print("📄 Archivos disponibles:", os.listdir())
print("📁 Contenido funciones/:", os.listdir("./funciones"))





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

@app.get("/kpis/mensual")
def get_kpis_mensuales(codsalon: str):
    try:
        df = cargar_hoja("1194190690")  # GID actualizado para mensual
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
    system_prompt = """
Eres Mont Dirección, una asistente especializada en el análisis de salones de belleza.

Tu objetivo es ayudar a las directoras a interpretar los resultados operativos, basándote exclusivamente en los siguientes KPIs:

- facturacionsiva: mide ingresos sin IVA.
- ratiodesviaciontiempoteorico: mide la diferencia entre el tiempo planificado y el tiempo realmente trabajado.
- ratiogeneral: relaciona la facturación con el coste del personal.
- ratioticketsinferior20: porcentaje de tickets con importe inferior a 20 €.
- ratiotiempoindirecto: porcentaje de tiempo no productivo (no atendiendo clientes).
- ticketsivamedio: importe medio por ticket (solo informativo).
- horasfichadas: tiempo total fichado (solo informativo).

Nunca menciones KPIs que no estén en esta lista.

📅 Analizas datos del **año 2025**.

Puedes explicar KPIs en tres niveles:
- 📌 Diario (requiere: codsalon y fecha).
- 📆 Semanal (requiere: codsalon y número de semana).
- 📊 Mensual (requiere: codsalon, mes y código del empleado).

📌 Si falta un dato, solicita amablemente la información antes de responder.

⚙️ Invoca las funciones disponibles automáticamente según el mensaje:
- explicar_ratio_diario
- explicar_ratio_semanal
- explicar_ratio_mensual

📎 Usa solo los datos proporcionados por el usuario o disponibles en los parámetros. No inventes información.

Tus respuestas deben ser claras, profesionales.
""".strip()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

      try:
        parametros_contexto = []

        if codsalon:
            parametros_contexto.append(f"codsalon: {codsalon}")
        if fecha:
            parametros_contexto.append(f"fecha: {fecha}")
        if nsemana:
            parametros_contexto.append(f"nsemana: {nsemana}")
        if mes:
            parametros_contexto.append(f"mes: {mes}")
        if codempleado:
            parametros_contexto.append(f"codempleado: {codempleado}")

        contexto_adicional = f"📎 Parámetros recibidos: {', '.join(parametros_contexto)}"

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": contexto_adicional},
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

