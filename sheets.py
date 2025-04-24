from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from sheets import (
    leer_kpis,
    analizar_salon,
    explicar_kpi,
    explicar_variacion,
    analizar_trabajadores,
    sugerencias_mejora,
)

app = FastAPI()

@app.get("/")
def home():
    return {"mensaje": "🟢 API Boot Directora funcionando correctamente"}

@app.get("/kpis")
def obtener_kpis(year: int = Query(...), nsemana: int = Query(...), codsalon: int = Query(...)):
    df = leer_kpis(year=year, nsemana=nsemana, codsalon=codsalon)
    return df.to_dict(orient="records")

@app.get("/kpis/salon/analisis")
def analisis_salon(year: int, nsemana: int, codsalon: int):
    df = leer_kpis(year=year, nsemana=nsemana, codsalon=codsalon)
    resultado = analizar_salon(df)
    return {"analisis": resultado}

@app.get("/kpis/explicar")
def explicacion_kpi(nombre: str = Query(...)):
    return {"kpi": nombre, "explicacion": explicar_kpi(nombre)}

@app.get("/kpis/variacion")
def comparar_semanas(year: int, nsemana_actual: int, nsemana_anterior: int, codsalon: int):
    df_actual = leer_kpis(year=year, nsemana=nsemana_actual, codsalon=codsalon)
    df_anterior = leer_kpis(year=year, nsemana=nsemana_anterior, codsalon=codsalon)
    resultado = explicar_variacion(df_actual, df_anterior)
    return {"variacion": resultado}

@app.get("/kpis/trabajadores")
def analisis_trabajadores(year: int, nsemana: int, codsalon: int):
    df = leer_kpis(year=year, nsemana=nsemana, codsalon=codsalon)
    resultado = analizar_trabajadores(df)
    return {"trabajadores": resultado}

@app.get("/kpis/sugerencias")
def sugerencias(year: int, nsemana: int, codsalon: int):
    df = leer_kpis(year=year, nsemana=nsemana, codsalon=codsalon)
    resultado = sugerencias_mejora(df)
    return resultado
