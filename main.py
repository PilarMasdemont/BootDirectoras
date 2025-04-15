from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from sheets import leer_kpis
import traceback

app = FastAPI()

@app.get("/kpis")
def obtener_kpis(
    year: int = Query(..., description="Año, por ejemplo 2025"),
    nsemana: int = Query(..., description="Número de semana"),
    codsalon: int = Query(..., description="Código de salón")
):
    try:
        data = leer_kpis(year=year, nsemana=nsemana, codsalon=codsalon)
        return {"kpis": data}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "trace": traceback.format_exc()}
        )

