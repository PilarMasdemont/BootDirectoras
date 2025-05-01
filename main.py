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

app = FastAPI()

@app.post("/chat")
async def chat_handler(request: Request):
    try:
        body = await request.json()
        mensaje_usuario = body.get("mensaje")

        if not mensaje_usuario:
            return JSONResponse(status_code=400, content={"error": "No se proporcionó ningún mensaje."})

        print("📩 Mensaje recibido:", mensaje_usuario)

        assistant_id = os.getenv("ASSISTANT_ID")
        if not assistant_id:
            return JSONResponse(status_code=500, content={"error": "Variable ASSISTANT_ID no está definida."})
        print("🧠 Assistant ID:", assistant_id)

        start_time = time.time()

        # Crear un nuevo thread
        thread = client.beta.threads.create()
        print("📂 Thread creado:", thread.id)

        # Añadir mensaje del usuario
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=mensaje_usuario
        )

        # Ejecutar el Assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
            instructions="Actúa como Mont Dirección, una asesora experta en KPIs de salones de peluquería."
        )
        print("🚀 Ejecutando run...")

        # Esperar la respuesta
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == "completed":
                print("✅ Run completado.")
                break
            elif run_status.status in ["failed", "cancelled"]:
                return JSONResponse(status_code=500, content={"error": f"Error en ejecución del assistant: {run_status.status}"})
            time.sleep(1)

        # Obtener el mensaje de respuesta
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        respuesta = messages.data[0].content[0].text.value if messages.data else None

        duration = time.time() - start_time
        print(f"⏱️ Tiempo total de respuesta: {duration:.2f}s")

        return {"respuesta": respuesta}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
