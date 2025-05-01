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
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.post("/chat")
async def chat_handler(request: Request):
    try:
        body = await request.json()
        mensaje_usuario = body.get("mensaje")

        if not mensaje_usuario:
            return JSONResponse(status_code=400, content={"error": "No se proporcionó ningún mensaje."})

        # Crear nuevo thread
        thread = client.beta.threads.create()

        # Añadir mensaje del usuario al thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=mensaje_usuario
        )

        # Lanzar ejecución con el Assistant ID
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=os.environ["ASSISTANT_ID"],
            instructions="Actúa como Mont Dirección, una asesora experta en KPIs de salones de peluquería."
        )

        return {"thread_id": thread.id, "run_id": run.id}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/chat/respuesta")
async def obtener_respuesta(thread_id: str, run_id: str):
    try:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )

        if run_status.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            respuesta = messages.data[0].content[0].text.value if messages.data else None
            return {"respuesta": respuesta}
        elif run_status.status in ["failed", "cancelled"]:
            return JSONResponse(status_code=500, content={"error": f"Ejecución fallida o cancelada: {run_status.status}"})
        else:
            return {"status": run_status.status}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
