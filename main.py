import os
import time
import json
import logging
import openai
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# ——— Logging de bajo nivel para OpenAI ———
openai.log = "debug"
logging.basicConfig(level=logging.DEBUG)

# ——— Carga de variables de entorno ———
load_dotenv()
API_KEY      = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

if not API_KEY:
    raise RuntimeError("Falta OPENAI_API_KEY")
if not ASSISTANT_ID:
    raise RuntimeError("Falta ASSISTANT_ID")

openai.api_key = API_KEY
client = openai.OpenAI()

app = FastAPI()

# ——— Tu función de ejemplo ———
def consultar_kpis(year: int, nsemana: int, codsalon: int, tipo: str = "semana") -> str:
    return (
        f"🔍 Datos simulados para el salón {codsalon}, semana {nsemana}, año {year}, tipo '{tipo}'. "
        "Ingresos: 1.500€, Clientes: 90, Ticket medio: 16,66€."
    )

# ——— Registra la función en tu Assistant (solo al arrancar) ———
# Esto hará que el Assistant «sepa» qué función puede invocar
print("🔧 Registrando funciones en el Assistant…", flush=True)
client.beta.assistants.update(
    assistant_id=ASSISTANT_ID,
    tools=[
        {
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
        }
    ]
)
print("✅ Funciones registradas.", flush=True)


@app.post("/chat")
async def chat_handler(request: Request):
    try:
        body = await request.json()
        mensaje_usuario = body.get("mensaje")
        if not mensaje_usuario:
            raise HTTPException(status_code=400, detail="No se proporcionó ningún mensaje.")

        # 1) Crea hilo y envía mensaje
        print("📌 Creando hilo…", flush=True)
        thread = client.beta.threads.create()
        print(f"→ Hilo creado: {thread.id}", flush=True)

        print("📤 Enviando mensaje al hilo…", flush=True)
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=mensaje_usuario
        )

        # 2) Lanza el run (sin 'functions', ya que la función está en el assistant)
        print("⚙️ Iniciando ejecución del Assistant…", flush=True)
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID,
            instructions="Actúa como Mont Dirección, una asesora experta en KPIs de salones de peluquería."
        )
        print(f"→ Run creado: {run.id}", flush=True)

        # 3) Polling
        while True:
            status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            st = status.to_dict() if hasattr(status, "to_dict") else status.__dict__
            print("↪ status completo:", json.dumps(st, indent=2, default=str), flush=True)

            if st.get("status") == "completed":
                break

            if st.get("status") == "requires_action":
                print("→ El Assistant pide llamar a una función", flush=True)
                for call in status.required_action.submit_tool_outputs.tool_calls:
                    if call.function.name == "consultar_kpis":
                        args = json.loads(call.function.arguments) if isinstance(call.function.arguments, str) else call.function.arguments
                        print(f"→ Llamando a consultar_kpis con args: {args}", flush=True)
                        result = consultar_kpis(**args)
                        client.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread.id,
                            run_id=run.id,
                            tool_outputs=[{"tool_call_id": call.id, "output": result}]
                        )
            elif st.get("status") in ("failed", "cancelled"):
                raise HTTPException(status_code=500, detail=f"Run terminó en '{st.get('status')}'")

            time.sleep(1)

        # 4) Recupera la respuesta final
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        respuesta = messages.data[-1].content[0].text.value if messages.data else "Sin respuesta."
        print(f"✅ Respuesta final: {respuesta}", flush=True)
        return {"respuesta": respuesta}

    except HTTPException:
        raise
    except Exception as e:
        print("❌ Error inesperado:", e, flush=True)
        raise HTTPException(status_code=500, detail=str(e))
