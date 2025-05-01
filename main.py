import os
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import OpenAI

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
        start = time.time()
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status in ["failed", "cancelled"]:
                return JSONResponse(status_code=500, content={"error": f"Error en ejecución del assistant: {run_status.status}"})
            time.sleep(1)

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        respuesta = messages.data[0].content[0].text.value if messages.data else None

        print(f"✅ RESPUESTA en {time.time() - start:.2f}s")
        return {"respuesta": respuesta}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
