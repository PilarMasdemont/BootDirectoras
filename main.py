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

        # Ejecutar el Assistant con definición de funciones
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=os.environ["ASSISTANT_ID"],
            instructions="Actúa como Mont Dirección, una asesora experta en KPIs de salones de peluquería.",
            functions=[{
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
            }]
        )

        # Esperar ejecución o responder con herramientas
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            print(f"Estado del run: {run_status.status}")

            if run_status.status == "completed":
                break
            elif run_status.status == "requires_action":
                print("→ El Assistant solicita llamar a una función")
                tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                for call in tool_calls:
                    if call.function.name == "consultar_kpis":
                        raw_args = call.function.arguments
                        args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                        print(f"→ Llamando a consultar_kpis con args: {args}")
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

        # Obtener respuesta final del Assistant
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        if messages.data:
            respuesta = messages.data[-1].content[0].text.value
        else:
            respuesta = "No hubo respuesta del Assistant."

        duration = time.time() - start_time
        print(f"✅ Respondido en {duration:.2f} segundos.")
        return {"respuesta": respuesta}

    except Exception as e:
        print(f"❌ Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
