from fastapi import FastAPI
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

