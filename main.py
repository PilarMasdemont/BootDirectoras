# main.py
import os
import time
import json
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import openai
from funciones import kpis

# Cargar variables de entorno
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

if not API_KEY or not ASSISTANT_ID:
    raise RuntimeError("Faltan variables de entorno necesarias.")

openai.log = "debug"
logging.basicConfig(level=logging.INFO)
client = openai.OpenAI(api_key=API_KEY)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat_handler(request: Request):
    try:
        data = await request.json()
        mensaje = data.get("mensaje")
        if not mensaje:
            raise HTTPException(status_code=400, detail="Falta el campo 'mensaje'.")

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
                    func = getattr(kpis, call.function.name, None)
                    if func:
                        output = func(**args)
                        outputs.append({"tool_call_id": call.id, "output": output})
                client.beta.threads.runs.submit_tool_outputs(thread_id=thread.id, run_id=run.id, tool_outputs=outputs)
            time.sleep(1)

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        for m in reversed(messages.data):
            if m.role == "assistant":
                respuesta = m.content[0].text.value
                break
        else:
            respuesta = "No se obtuvo respuesta del asistente."

        return {"respuesta": respuesta}

    except Exception as e:
        logging.exception("Error en /chat")
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud.")
