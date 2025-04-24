from fastapi import FastAPI, HTTPException
from sheets import leer_kpis, analizar_salon

app = FastAPI()

@app.get("/kpis")
def obtener_datos_crudos(year: int, nsemana: int, codsalon: int):
    try:
        df = leer_kpis(year=year, nsemana=nsemana, codsalon=codsalon, tipo="semana")
        return {"kpis": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kpis/salon/analisis")
def obtener_analisis_salon(year: int, nsemana: int, codsalon: int):
    try:
        df = leer_kpis(year=year, nsemana=nsemana, codsalon=codsalon, tipo="semana")
        resultado = analizar_salon(df)
        return {"analisis": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
