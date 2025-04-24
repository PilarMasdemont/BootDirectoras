from fastapi import FastAPI, Query
from sheets import leer_kpis, analizar_salon

app = FastAPI()

@app.get("/kpis")
def obtener_datos_crudos(
    year: int = Query(None), 
    nsemana: int = Query(None), 
    codsalon: int = Query(None)
):
    df = leer_kpis(year=year, nsemana=nsemana, codsalon=codsalon, tipo="semana")
    return {"kpis": df.to_dict(orient="records")}


@app.get("/kpis/salon/analisis")
def obtener_analisis_salon(
    year: int, 
    nsemana: int, 
    codsalon: int
):
    df = leer_kpis(year=year, nsemana=nsemana, codsalon=codsalon, tipo="semana")
    try:
        resultado = analizar_salon(df)
        return {"analisis": resultado}
    except Exception as e:
        return {"analisis": {"error": str(e)}}
