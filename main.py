import os
import time
import json
import logging
import openai
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Carga variables de entorno
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

if not API_KEY:
    raise RuntimeError("La variable de entorno OPENAI_API_KEY no está configurada.")
if not ASSISTANT_ID:
    raise RuntimeError("La variable de entorno ASSISTANT_ID no está configurada.")

# Logging de depuración para OpenAI
openai.log = "debug"
logging.basicConfig(level=logging.DEBUG)

# Inicializa cliente OpenAI
client = openai.OpenAI(api_key=API_KEY)

# Crea la app y habilita CORS para permitir peticiones desde tu frontend
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia "*" por el dominio de Crisp si quieres restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Función de ejemplo registrada en el Assistant
def consultar_kpis(year: int, nsemana: int, codsalon: int, tipo: str = "semana") -> str:
    # Aquí conectarías a tu hoja de cálculo o base de datos
    return (
        f"🔍 Datos simulados para el salón {codsalon}, semana {nsemana}, año {year}, tipo '{tipo}'. "
        f"Ingresos: 1.500€, Clientes: 90, Ticket medio: 16,66€."
    )

# Registra la función en el Assistant al arrancar la aplicación
@app.on_event("startup")
def register_functions():
    tools = [{
        "type": "function",
        "function": {
            "name": "consultar_kpis",
            "description": "Obtiene KPIs de la hoja de cálculo para un salón, semana y año dados",
            "parameters": {
                "type": "object",
                "properties": {
                    "year":     {"type": "integer"},
                    "nsemana":  {"type": "integer"},
                    "codsalon": {"type": "integer"},
                    "tipo": {
                        "type": "string",
                        "enum": ["semana", "trabajadores", "mensual", "mensual_comparado"]
                    }
                },
                "required": ["year", "nsemana", "codsalon"]
            }
        }
    }]
    logging.info("Registrando herramientas en Assistant %s", ASSISTANT_ID)
    client.beta.assistants.update(
        assistant_id=ASSISTANT_ID,
        tools=tools
    )
    logging.info("Herramientas registradas correctamente.")

@app.post("/chat")
async def chat_handler(request: Request):
    body = await request.json()
    mensaje = body.get("mensaje")
    if not mensaje:
        raise HTTPException(status_code=400, detail="Debe enviar un campo 'mensaje'.")

    # Crea hilo y envía el mensaje del usuario
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=mensaje
    )

    # Inicia ejecución del Assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID,
        instructions="Actúa como Mont Dirección, experta en KPIs de salones de peluquería."
    )

    # Polling hasta finalización o llamada a función
    while True:
        status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        st = status.to_dict() if hasattr(status, 'to_dict') else status.__dict__
        if st.get("status") == "completed":
            break
        if st.get("status") == "requires_action":
            for call in status.required_action.submit_tool_outputs.tool_calls:
                if call.function.name == "consultar_kpis":
                    args = json.loads(call.function.arguments)
                    result = consultar_kpis(**args)
                    client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=[{"tool_call_id": call.id, "output": result}]
                    )
        time.sleep(1)

    # Recupera la respuesta final del thread
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    last = messages.data[-1] if messages.data else None
    respuesta = last.content[0].text.value if last and last.content else ""
    return {"respuesta": respuesta}
