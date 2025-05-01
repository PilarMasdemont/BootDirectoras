import time
import json
import logging
import openai

# Configurar logging de depuración
openai.log = "debug"
logging.basicConfig(level=logging.DEBUG)

# --------------------------------------------------
#  DEFINICIÓN DIRECTA DE CREDENCIALES (para ejecución local)
#  ⚠️ IMPORTANTE: reemplaza los siguientes valores con tus credenciales reales
API_KEY = "reemplaza_con_tu_api_key"
ASSISTANT_ID = "reemplaza_con_tu_assistant_id"
# --------------------------------------------------

if API_KEY == "reemplaza_con_tu_api_key" or ASSISTANT_ID == "reemplaza_con_tu_assistant_id":
    raise RuntimeError(
        "Debes reemplazar API_KEY y ASSISTANT_ID en las variables al inicio del script con tus valores reales."
    )

# Inicializar cliente con api_key explícito
try:
    client = openai.OpenAI(api_key=API_KEY)
except Exception as e:
    print(f"❌ Error al inicializar OpenAI client: {e}")
    raise

# Registrar la función en el Assistant (solo una vez al arrancar)
print("🔧 Registrando la función 'consultar_kpis' en el Assistant…", flush=True)
try:
    client.beta.assistants.update(
        assistant_id=ASSISTANT_ID,
        tools=[{
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
    )
    print("✅ Función registrada.", flush=True)
except Exception as e:
    print(f"❌ Falló registro de función: {e}")
    raise

# Definir la función simulada localmente
def consultar_kpis(year, nsemana, codsalon, tipo="semana"):
    return (
        f"🔍 Datos simulados para el salón {codsalon}, semana {nsemana}, año {year}, tipo '{tipo}'. "
        "Ingresos: 1.500€, Clientes: 90, Ticket medio: 16,66€."
    )

# Inicio del flujo de chat
start_time = time.time()

print("📌 Creando hilo…", flush=True)
thread = client.beta.threads.create()
print(f"→ Hilo creado: id={thread.id}", flush=True)

# Enviar mensaje de usuario
definir_mensaje = "Hola, ¿cómo fue la semana pasada en el salón 1?"
print("📤 Enviando mensaje…", flush=True)
client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=definir_mensaje
)
print(f"→ Mensaje enviado: '{definir_mensaje}'", flush=True)

# Ejecutar el Assistant (sin pasar 'functions', ya está registrado)
print("⚙️ Iniciando ejecución del Assistant…", flush=True)
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=ASSISTANT_ID,
    instructions="Actúa como Mont Dirección, una asesora experta en KPIs de salones de peluquería."
)
print(f"→ Run creado: id={run.id}", flush=True)

# Polling hasta que termine o requiera acción
while True:
    status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    st = status.to_dict() if hasattr(status, 'to_dict') else status.__dict__
    print("↪ status completo:", json.dumps(st, indent=2, default=str), flush=True)

    if st.get('status') == 'completed':
        print("✅ Run completado", flush=True)
        break

    if st.get('status') == 'requires_action':
        print("→ El Assistant solicita llamar a una función", flush=True)
        for call in status.required_action.submit_tool_outputs.tool_calls:
            if call.function.name == 'consultar_kpis':
                args = json.loads(call.function.arguments) if isinstance(call.function.arguments, str) else call.function.arguments
                print(f"→ Llamando a consultar_kpis con args: {args}", flush=True)
                result = consultar_kpis(**args)
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=[{'tool_call_id': call.id, 'output': result}]
                )
    elif st.get('status') in ['failed', 'cancelled']:
        print(f"❌ Run terminó en estado: {st.get('status')}", flush=True)
        exit(1)

    time.sleep(1)

# Obtener la respuesta final
tokens = client.beta.threads.messages.list(thread_id=thread.id)
if tokens.data:
    respuesta = tokens.data[-1].content[0].text.value
else:
    respuesta = 'No hubo respuesta.'

print(f"\n✅ RESPUESTA en {time.time() - start_time:.2f}s:\n{respuesta}", flush=True)
