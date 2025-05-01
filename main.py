import os
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import OpenAI
from openai.types.beta.threads import RunToolCall
import json
import requests

app = FastAPI()

# Inicializar cliente OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.get("/")
def root():
    return {"message": "API BootDirectoras funcionando"}

@app.post("/chat")
async def chat_handler(request: Request):
    try:
        body = await request.json()
        mensaje_usuario = body.get("mensaje")

        if not mensaje_usuario:
            return JSONResponse(status_code=400, content={"error": "No se proporcionó ningún mensaje."})

        print("📌 Creando hilo...")
        thread = client.beta.threads.create()

        print("📤 Enviando mensaje al hilo...")
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=mensaje_usuario
        )

        print("⚙️ Iniciando ejecución del Assistant...")
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=os.environ["ASSISTANT_ID"],
            instructions="Actúa como Mont Dirección, una asesora experta en KPIs de salones de peluquería."
        )

        print("⏳ Esperando respuesta...")
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run_status.status == "completed":
                break
            elif run_status.status == "requires_action":
                tool_call = run_status.required_action.submit_tool_outputs.tool_calls[0]
                if tool_call.function.name == "consultar_kpis":
                    args = json.loads(tool_call.function.arguments)
                    resultado = consultar_kpis(**args)
                    client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=[{
                            "tool_call_id": tool_call.id,
                            "output": json.dumps(resultado)
                        }]
                    )
            elif run_status.status in ["failed", "cancelled"]:
                return JSONResponse(status_code=500, content={"error": f"Error en ejecución del assistant: {run_status.status}"})
            time.sleep(1)

        # Obtener mensaje de respuesta
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        respuesta = messages.data[0].content[0].text.value if messages.data else "No se obtuvo respuesta."

        return {"respuesta": respuesta}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Definición de la función que será usada como tool
def consultar_kpis(year: int, codsalon: int, nsemana: int, tipo: str):
    url = "https://bootdirectoras.onrender.com/kpis"
    params = {
        "year": year,
        "codsalon": codsalon,
        "nsemana": nsemana,
        "tipo": tipo
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"No se pudo obtener datos. Status: {response.status_code}"}

