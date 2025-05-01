import time
import json
from openai import OpenAI

# Inicializa el cliente con tu clave API
client = OpenAI(api_key="sk-proj-ExBq3SYCxiFgUkWpnOYVvD_TYh2yyzJ...KoyTjo_ZD_aygeT9aayNLTp4peu10XC5uV0yUuA_ZA9MZVV_BAgiWNyJeLcOsA")

# Define tu Assistant ID
assistant_id = "asst_4Nm4s1R16uypzT560FHvHzYj"

# Función para consultar KPIs (simulación)
def consultar_kpis(year, nsemana, codsalon, tipo):
    return (
        f"🔍 Datos simulados para el salón {codsalon}, semana {nsemana}, año {year}, tipo '{tipo}'. "
        f"Ingresos: 1.500€, Clientes: 90, Ticket medio: 16,66€."
    )

start = time.time()

# Crea un hilo de conversación
print("📌 Creando hilo...")
thread = client.beta.threads.create()

# Envía el mensaje del usuario
definir_mensaje = "Hola, ¿cómo fue la semana pasada en el salón 1?"
print("📤 Enviando mensaje al hilo...")
client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=definir_mensaje
)

# Ejecuta el Assistant con definición de funciones
print("⚙️ Iniciando ejecución del Assistant...")
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant_id,
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

# Espera hasta que se complete o requiera acción
while True:
    status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    print(f"Estado del run: {status.status}")

    if status.status == "completed":
        break
    
    if status.status == "requires_action":
        print("→ El Assistant solicita llamar a una función")
        tool_calls = status.required_action.submit_tool_outputs.tool_calls
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
        # Envía la respuesta de la función de vuelta al Assistant
        client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )
    
    if status.status in ["failed", "cancelled"]:
        print(f"❌ Falló la ejecución: {status.status}")
        exit(1)

    time.sleep(1)

# Extrae y muestra la respuesta final
messages = client.beta.threads.messages.list(thread_id=thread.id)
if messages.data:
    respuesta = messages.data[-1].content[0].text.value
else:
    respuesta = "No hubo respuesta del Assistant."

print(f"\n✅ RESPUESTA en {time.time() - start:.2f}s:\n{respuesta}")
