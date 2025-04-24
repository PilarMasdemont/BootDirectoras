from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from sheets import leer_kpis
import traceback

app = FastAPI()

@app.get("/kpis")
def obtener_kpis(
    year: int = Query(None),
    nsemana: int = Query(None),
    codsalon: int = Query(None),
    tipo: str = Query("semana")
):
    try:
        df = leer_kpis(year=year, nsemana=nsemana, codsalon=codsalon, tipo=tipo)
        return {"datos": df.to_dict(orient="records")}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e), "trace": traceback.format_exc()})
