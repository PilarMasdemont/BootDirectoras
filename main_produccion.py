import os
import time
import json
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import openai

# === Cargar variables de entorno ===
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

if not API_KEY or not ASSISTANT_ID:
    raise RuntimeError("Faltan variables de entorno necesarias.")

# === Cliente y logging ===
openai.log = "debug"
logging.basicConfig(level=logging.INFO)
client = openai.OpenAI(api_key=API_KEY)

# === Importar funciones ===
from funciones.kpis import consultar_kpis
from funciones.analizar_salon import analizar_salon
from funciones.analizar_trabajadores import analizar_trabajadores
from funciones.explicar_kpi import explicar_kpi
from funciones.explicar_variacion import explicar_variacion
from funciones.sugerencias_mejora import sugerencias_mejora

# === FastAPI setup ===
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Usa tu dominio real en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Registrar funciones ===
@app.on_event("startup")
def registrar_funciones():
    logging.info("Registrando funciones...")
    tools = []
    funciones = [
        consultar_kpis,
        analizar_salon,
        analizar_trabajadores,
        explicar_kpi,
        explicar_variacion,
        sugerencias_mejora,
    ]
    for fn in funciones:
        tools.append({
            "type": "function",
            "function": {
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
            }
        })

    client.beta.assistants.update(assistant_id=ASSISTANT_ID, tools=tools)
    logging.info("✅ Funciones registradas correctamente.")

# === Endpoint principal del asistente ===
@app.post("/chat")
async def chat_handler(request: Request):
    try:
        data = await request.json()
        mensaje = data.get("mensaje")
        if not mensaje:
            raise HTTPException(status_code=400, detail="Falta el campo 'mensaje'.")

        logging.info("➡️ Mensaje recibido: %s", mensaje)

        thread = client.beta.threads.create()
        client.beta.threads.messages.create(thread_id=thread.id, role="user", content=mensaje)

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID,
            instructions="Actúa como Mont Dirección, experta en KPIs de salones de peluquería."
        )

        while True:
            status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if status.status == "completed":
                break
            if status.status == "requires_action":
                tool_calls = status.required_action.submit_tool_outputs.tool_calls
                outputs = []
                for call in tool_calls:
                    nombre_funcion = call.function.name
                    args = json.loads(call.function.arguments)
                    logging.info(f"🛠 Ejecutando: {nombre_funcion} con {args}")

                    # Ejecutar la función correspondiente
                    if nombre_funcion == "consultar_kpis":
                        result = consultar_kpis(**args)
                    elif nombre_funcion == "analizar_salon":
                        result = analizar_salon(**args)
                    elif nombre_funcion == "analizar_trabajadores":
                        result = analizar_trabajadores(**args)
                    elif nombre_funcion == "explicar_kpi":
                        result = explicar_kpi(**args)
                    elif nombre_funcion == "explicar_variacion":
                        result = explicar_variacion(**args)
                    elif nombre_funcion == "sugerencias_mejora":
                        result = sugerencias_mejora(**args)
                    else:
                        result = f"⚠️ Función desconocida: {nombre_funcion}"

                    outputs.append({"tool_call_id": call.id, "output": result})

                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=outputs
                )
            time.sleep(1)

        # Obtener la respuesta del asistente
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        for m in reversed(messages.data):
            if m.role == "assistant":
                return {"respuesta": m.content[0].text.value}
        return {"respuesta": "⚠️ No se obtuvo respuesta del asistente."}

    except Exception as e:
        logging.exception("❌ Error al procesar el mensaje")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")
