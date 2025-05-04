import os
import time
import json
import logging
import openai
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Importa tus funciones
from funciones.kpis import consultar_kpis
from funciones.analizar_salon import analizar_salon
from funciones.analizar_trabajadores import analizar_trabajadores
from funciones.explicar_kpi import explicar_kpi
from funciones.explicar_variacion import explicar_variacion
from funciones.sugerencias_mejora import sugerencias_mejora

# Carga variables de entorno
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

if not API_KEY or not ASSISTANT_ID:
    raise RuntimeError("❌ Faltan las variables OPENAI_API_KEY o ASSISTANT_ID")

# Configuración de logging
openai.log = "debug"
logging.basicConfig(level=logging.INFO)
client = openai.OpenAI(api_key=API_KEY)

# App FastAPI + CORS
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de funciones al iniciar
@app.on_event("startup")
def registrar_funciones():
    funciones = [
        consultar_kpis,
        analizar_salon,
        analizar_trabajadores,
        explicar_kpi,
        explicar_variacion,
        sugerencias_mejora
    ]
    tools = [
        {
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
        }
        for fn in funciones
    ]
    client.beta.assistants.update(assistant_id=ASSISTANT_ID, tools=tools)
    logging.info("✅ Funciones registradas correctamente.")

# Endpoint principal
@app.post("/chat")
async def chat_handler(request: Request):
    try:
        body = await request.json()
        mensaje = body.get("mensaje")
        if not mensaje:
            raise HTTPException(status_code=400, detail="Falta el campo 'mensaje'.")

        logging.info("➡️ Mensaje recibido: %s", mensaje)

        thread = client.beta.threads.create()
        client.beta.threads.messages.create(thread_id=thread.id, role="user", content=mensaje)

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID,
            instructions=(
                "Contesta siempre con un saludo, y presentándote: Soy Mont Dirección.\n\n"
                "Eres un asistente especializado en ayudar a directoras de salones de peluquería. "
                "Tu función es ayudarles a entender cómo mejorar su negocio.\n\n"
                "Después de llamar a una función y recibir su respuesta, escribe siempre una respuesta explicativa "
                "para la directora del salón en español claro y directo.\n\n"
                "⚠️ Usa los nombres de los parámetros exactamente como están definidos en las funciones: 'year', 'nsemana', 'codsalon', etc.\n\n"
                "🗓️ Asume que el año actual es 2025 salvo que se indique lo contrario. Interpreta frases como 'esta semana', 'el mes pasado', etc."
            )
        )

        while True:
            status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if status.status == "completed":
                break
            if status.status == "requires_action":
                outputs = []
                for call in status.required_action.submit_tool_outputs.tool_calls:
                    args = json.loads(call.function.arguments)
                    nombre_funcion = call.function.name
                    logging.info("🛠 Ejecutando %s con argumentos %s", nombre_funcion, args)

                    if nombre_funcion == "consultar_kpis":
                        resultado = consultar_kpis(**args)
                    elif nombre_funcion == "analizar_salon":
                        resultado = analizar_salon(**args)
                    elif nombre_funcion == "analizar_trabajadores":
                        resultado = analizar_trabajadores(**args)
                    elif nombre_funcion == "explicar_kpi":
                        resultado = explicar_kpi(**args)
                    elif nombre_funcion == "explicar_variacion":
                        resultado = explicar_variacion(**args)
                    elif nombre_funcion == "sugerencias_mejora":
                        resultado = sugerencias_mejora(**args)
                    else:
                        resultado = "⚠️ Función no reconocida."

                    outputs.append({"tool_call_id": call.id, "output": resultado})

                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id, run_id=run.id, tool_outputs=outputs
                )
            time.sleep(1)

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        for m in reversed(messages.data):
            if m.role == "assistant":
                return {"respuesta": m.content[0].text.value}
        return {"respuesta": "⚠️ No se obtuvo respuesta del asistente."}

    except Exception as e:
        logging.exception("❌ Error en el procesamiento del asistente")
        raise HTTPException(status_code=500, detail="Error interno al procesar la solicitud.")
