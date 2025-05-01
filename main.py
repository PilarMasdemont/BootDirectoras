import os
import time
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Simulación de la función registrada en el Assistant
def consultar_kpis(year, nsemana, codsalon, tipo):
    return (
        f"🔍 Datos simulados para el salón {codsalon}, semana {nsemana}, año {year}, tipo '{tipo}'. "
        f"Ingresos: 1.500€, Clientes: 90, Ticket medio: 16,66€."
    )

@app.post("/chat")
async def chat_handler(request: Request):
    try:
        body = await request.json()
        mensaje_usuario = body.get("mensaje")

        if not mensaje_usuario:
            return JSONResponse(status_code=400, content={"error": "No se proporcionó ningún mensaje."})

        print(f"🟢 Mensaje recibido: {mensaje_usuario}")
        start_time = time.time()

        # Crear hilo
        thread = client.beta.threads.create()

        # Enviar mensaje del usuario
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=mensaje_usuario
        )

        # Ejecutar el Assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=os.environ["ASSISTANT_ID"],
            instructions="Actúa como Mont Dirección, una asesora experta en KPIs de salones de peluquería."
        )

        # Esperar ejecución o responder con tools
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

            if run_status.status == "completed":
                break
            elif run_status.status == "requires_action":
                tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []

                for call in tool_calls:
                    if call.function.name == "consultar_kpis":
                        args = json.loads(call.function.arguments)
                        result = consultar_kpis(**args)
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
                return JSONResponse(status_code=500, content={"error": f"Error en ejecución: {run_status.status}"})

            time.sleep(1)

        # Obtener respuesta
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        respuesta = messages.data[0].content[0].text.value if messages.data else "No hubo respuesta."

        duration = time.time() - start_time
        print(f"✅ Respondido en {duration:.2f} segundos.")
        return {"respuesta": respuesta}

    except Exception as e:
        print(f"❌ Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
