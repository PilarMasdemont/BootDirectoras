import os
import time
import json
import logging
import openai
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Importa funciones personalizadas
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

if not API_KEY:
    raise RuntimeError("La variable de entorno OPENAI_API_KEY no está configurada.")
if not ASSISTANT_ID:
    raise RuntimeError("La variable de entorno ASSISTANT_ID no está configurada.")

# Configuración de logging
openai.log = "debug"
logging.basicConfig(level=logging.DEBUG)

# Inicializa cliente OpenAI
client = openai.OpenAI(api_key=API_KEY)

# Crea la app y configura CORS
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de funciones en el Assistant
@app.on_event("startup")
def register_functions():
    functions = [
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
        } for fn in [
            consultar_kpis, analizar_salon, analizar_trabajadores,
            explicar_kpi, explicar_variacion, sugerencias_mejora
        ]
    ]

    logging.info("Registrando funciones en el assistant %s", ASSISTANT_ID)
    client.beta.assistants.update(
        assistant_id=ASSISTANT_ID,
        tools=functions
    )
    logging.info("Funciones registradas correctamente.")

# Ruta principal del chat
@app.post("/chat")
async def chat_handler(request: Request):
    body = await request.json()
    mensaje = body.get("mensaje")
    if not mensaje:
        raise HTTPException(status_code=400, detail="Debe enviar un campo 'mensaje'.")

    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=mensaje
    )

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
            outputs = []
            for call in status.required_action.submit_tool_outputs.tool_calls:
                nombre_funcion = call.function.name
                argumentos = json.loads(call.function.arguments)

                resultado = ""
                if nombre_funcion == "consultar_kpis":
                    resultado = consultar_kpis(**argumentos)
                elif nombre_funcion == "analizar_salon":
                    resultado = analizar_salon(**argumentos)
                elif nombre_funcion == "analizar_trabajadores":
                    resultado = analizar_trabajadores(**argumentos)
                elif nombre_funcion == "explicar_kpi":
                    resultado = explicar_kpi(**argumentos)
                elif nombre_funcion == "explicar_variacion":
                    resultado = explicar_variacion(**argumentos)
                elif nombre_funcion == "sugerencias_mejora":
                    resultado = sugerencias_mejora(**argumentos)

                outputs.append({"tool_call_id": call.id, "output": resultado})

            client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=outputs
            )
        time.sleep(1)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    last = messages.data[-1] if messages.data else None

    respuesta = ""
    if last and last.content:
        for item in last.content:
            if item.type == "text":
                respuesta = item.text.value
                break

    print("MENSAJE FINAL DEL BOT:", respuesta)  # Debug útil en logs
    return {"respuesta": respuesta or "No se recibió respuesta del asistente."}
