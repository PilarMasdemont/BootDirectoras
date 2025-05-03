import os
import time
import json
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import openai

# Cargar variables de entorno
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

if not API_KEY or not ASSISTANT_ID:
    raise RuntimeError("Faltan variables de entorno necesarias.")

# Configura logging y cliente
openai.log = "debug"
logging.basicConfig(level=logging.INFO)
client = openai.OpenAI(api_key=API_KEY)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar por tu dominio en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulación de función (puede venir de un módulo externo)
def consultar_kpis(year: int, nsemana: int, codsalon: int, tipo: str = "semana") -> str:
    return (
        f"🔍 Datos simulados para el salón {codsalon}, semana {nsemana}, año {year}, tipo '{tipo}'. "
        f"Ingresos: 1.500€, Clientes: 90, Ticket medio: 16,66€."
    )

@app.on_event("startup")
def registrar_funciones():
    logging.info("Registrando función 'consultar_kpis'...")
    tools = [
        {
            "type": "function",
            "function": {
                "name": "consultar_kpis",
                "description": "Obtiene KPIs de la hoja de cálculo para un salón, semana y año dados",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "year": {"type": "integer"},
                        "nsemana": {"type": "integer"},
                        "codsalon": {"type": "integer"},
                        "tipo": {
                            "type": "string",
                            "enum": ["semana", "trabajadores", "mensual", "mensual_comparado"],
                        },
                    },
                    "required": ["year", "nsemana", "codsalon"],
                },
            },
        }
    ]
    client.beta.assistants.update(assistant_id=ASSISTANT_ID, tools=tools)
    logging.info("✅ Función registrada correctamente.")

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
                    args = json.loads(call.function.arguments)
                    logging.info("🛠 Ejecutando función: consultar_kpis con %s", args)
                    output = consultar_kpis(**args)
                    outputs.append({"tool_call_id": call.id, "output": output})
                client.beta.threads.runs.submit_tool_outputs(thread_id=thread.id, run_id=run.id, tool_outputs=outputs)
            time.sleep(1)

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        for m in reversed(messages.data):
            if m.role == "assistant":
                respuesta = m.content[0].text.value
                break
        else:
            respuesta = "⚠️ No se obtuvo respuesta del asistente."

        return {"respuesta": respuesta}

    except Exception as e:
        logging.exception("❌ Error en la ejecución del asistente")
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud.")
