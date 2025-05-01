from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import OpenAI
import os
import time
from sheets import (
    leer_kpis,
    analizar_salon,
    explicar_kpi,
    explicar_variacion,
    analizar_trabajadores,
    sugerencias_mejora
)

app = FastAPI()

@app.get("/kpis")
def kpis(year: int = None, nsemana: int = None, codsalon: int = None):
    df = leer_kpis(year=year, nsemana=nsemana, codsalon=codsalon)
    return {"salon": analizar_salon(df)}

@app.get("/kpis/salon/analisis")
def analisis_salon(year: int = None, nsemana: int = None, codsalon: int = None):
    df = leer_kpis(year=year, nsemana=nsemana, codsalon=codsalon)
    return analizar_salon(df)

@app.get("/kpis/explicar")
def explicar(nombre: str):
    return {"kpi": nombre, "explicacion": explicar_kpi(nombre)}

@app.get("/kpis/variacion")
def variacion(year: int, nsemana_actual: int, nsemana_anterior: int, codsalon: int):
    df_actual = leer_kpis(year=year, nsemana=nsemana_actual, codsalon=codsalon)
    df_anterior = leer_kpis(year=year, nsemana=nsemana_anterior, codsalon=codsalon)
    return {"variacion": explicar_variacion(df_actual, df_anterior)}

@app.get("/kpis/trabajadores")
def trabajadores(year: int = None, nsemana: int = None, codsalon: int = None):
    df = leer_kpis(year=year, nsemana=nsemana, codsalon=codsalon, tipo="trabajadores")
    return {"trabajadores": analizar_trabajadores(df)}

@app.get("/kpis/sugerencias")
def sugerencias(year: int = None, nsemana: int = None, codsalon: int = None):
    df = leer_kpis(year=year, nsemana=nsemana, codsalon=codsalon)
    return sugerencias_mejora(df)

@app.get("/kpis/mensual_comparado")
def consultar_kpis_mensual_comparado(
    year: int = None,
    codsalon: int = None
):
    df = leer_kpis(year=year, codsalon=codsalon, tipo="mensual_comparado")
    return df.to_dict(orient="records")


# Inicializar cliente OpenAI con API Key desde variable de entorno
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/chat")
async def chat_handler(request: Request):
    try:
        body = await request.json()
        mensaje_usuario = body.get("mensaje")
        print("📩 Mensaje recibido:", mensaje_usuario)

        if not mensaje_usuario:
            return JSONResponse(status_code=400, content={"error": "No se proporcionó ningún mensaje."})

        start_time = time.time()

        print("📥 Creando thread...")
        thread = client.beta.threads.create()
        print("✅ Thread creado:", thread.id)

        print("📝 Añadiendo mensaje del usuario...")
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=mensaje_usuario
        )
        print("✅ Mensaje añadido")

        print("🚀 Lanzando run...")
        assistant_id = os.environ.get("ASSISTANT_ID")
        if not assistant_id:
            return JSONResponse(status_code=500, content={"error": "ASSISTANT_ID no está definido en variables de entorno."})

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
            instructions="Actúa como Mont Dirección, asesora experta en salones."
        )
        print("🕒 Run iniciado:", run.id)

        max_wait = 60
        waited = 0
        while waited < max_wait:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            print("⏳ Estado del run:", run_status.status)
            if run_status.status == "completed":
                break
            elif run_status.status in ["failed", "cancelled"]:
                return JSONResponse(status_code=500, content={"error": f"Error en ejecución del assistant: {run_status.status}"})
            time.sleep(2)
            waited += 2
        else:
            return JSONResponse(status_code=500, content={"error": "Timeout esperando la respuesta del assistant."})

        print("📤 Obteniendo mensaje del assistant...")
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        respuesta = messages.data[0].content[0].text.value if messages.data else None

        duration = time.time() - start_time
        print(f"⏱️ Tiempo total de respuesta: {duration:.2f}s")
        print("💬 Respuesta:", respuesta)

        return {"respuesta": respuesta}

    except Exception as e:
        print("❌ Excepción capturada:", str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})
