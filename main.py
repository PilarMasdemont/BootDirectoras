from fastapi import FastAPI, Request
from openai import OpenAI
import os
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


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.post("/chat")
async def chat_handler(request: Request):
    body = await request.json()
    user_message = body.get("message", "")

    response = client.chat.completions.create(
        model="gpt-4",  # o el modelo que uses
        messages=[
            {
                "role": "system",
                "content": "Eres un asistente experto en KPIs de salones de peluquería."
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "consultar_kpis",
                    "description": "Consulta los KPIs del salón para una semana, mes o trabajador.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "year": {"type": "integer"},
                            "nsemana": {"type": "integer"},
                            "codsalon": {"type": "integer"},
                            "tipo": {
                                "type": "string",
                                "enum": ["semana", "mensual", "trabajadores"]
                            }
                        },
                        "required": ["year", "codsalon", "nsemana"]
                    }
                }
            }
        ],
        tool_choice="auto"
    )

    return {"respuesta": response.choices[0].message.content}
