import os
import time
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Simulador de función conectada al Assistant
def leer_kpis(salon_id):
    return f"KPI simulado del salón {salon_id}"

@app.post("/chat")
async def chat_handler(request: Request):
    try:
        body = await request.json()
        mensaje_usuario = body.get("mensaje")

        if not mensaje_usuario:
            return JSONResponse(status_code=400, content={"error": "No se proporcionó ningún mensaje."})

        start_time = time.time()
        print("📩 Mensaje recibido:", mensaje_usuario)

        # Crear hilo y mensaje
        thread = client.beta.threads.create()
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=mensaje_usuario
        )

        # Lanzar ejecución del Assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=os.environ["ASSISTANT_ID"],
            instructions="Actúa como Mont Dirección, una asesora experta en KPIs de salones de peluquería."
        )

        # Esperar o actuar según el estado
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

            if run_status.status == "completed":
                break

            elif run_status.status == "requires_action":
                tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []

                for call in tool_calls:
                    if call.function.name == "leer_kpis":
                        args = json.loads(call.function.arguments)
                        result = leer_kpis(**args)

                        tool_outputs.append({
                            "tool_call_id": call.id,
                            "output": result
                        })

                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

            elif run_status.status in ["failed", "cancelled"]:
                return JSONResponse(status_code=500, content={"error": f"Assistant falló: {run_status.status}"})

            time.sleep(1)

        # Obtener la respuesta final
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        respuesta = messages.data[0].content[0].text.value if messages.data else "Sin respuesta."

        print(f"✅ Respuesta en {time.time() - start_time:.2f}s")
        return {"respuesta": respuesta}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

        return {"error": f"No se pudo obtener datos. Status: {response.status_code}"}

