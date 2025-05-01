import os
import time
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from openai import OpenAI
from openai.error import AuthenticationError

# Carga variables de entorno
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

if not API_KEY:
    raise RuntimeError("La variable de entorno OPENAI_API_KEY no está configurada.")
if not ASSISTANT_ID:
    raise RuntimeError("La variable de entorno ASSISTANT_ID no está configurada.")

app = FastAPI()
client = OpenAI(api_key=API_KEY)

# Función de ejemplo registrada en el Assistant
def consultar_kpis(year: int, nsemana: int, codsalon: int, tipo: str = "semana") -> str:
    # Aquí conectarías a tu hoja de cálculo o base de datos
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
            raise HTTPException(status_code=400, detail="No se proporcionó ningún mensaje.")

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
            assistant_id=ASSISTANT_ID,
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

        # Esperar hasta que termine o solicite acción
        while True:
            status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            print(f"Estado del run: {status.status}")

            if status.status == "completed":
                break

            if status.status == "requires_action":
                print("→ El Assistant solicita llamar a una función")
                tool_calls = status.required_action.submit_tool_outputs.tool_calls
                outputs = []
                for call in tool_calls:
                    if call.function.name == "consultar_kpis":
                        args = json.loads(call.function.arguments) if isinstance(call.function.arguments, str) else call.function.arguments
                        print(f"→ Llamando a consultar_kpis con args: {args}")
                        result = consultar_kpis(**args)
                        outputs.append({"tool_call_id": call.id, "output": result})
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=outputs
                )

            if status.status in ["failed", "cancelled"]:
                raise HTTPException(status_code=500, detail=f"Error en ejecución: {status.status}")
            time.sleep(1)

        # Obtener y devolver la respuesta final
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        respuesta = messages.data[-1].content[0].text.value if messages.data else "No hubo respuesta del Assistant."
        print(f"✅ Respuesta: {respuesta}")
        return {"respuesta": respuesta}

    except AuthenticationError as e:
        print(f"❌ AuthenticationError: {e}")
        raise HTTPException(status_code=500, detail="Error de autenticación con OpenAI. Verifica tu API key.")
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        raise HTTPException(status_code=500, detail=str(e))
