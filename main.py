from fastapi import FastAPI, Query
from sheets import leer_kpis
from fastapi.responses import JSONResponse
import traceback

app = FastAPI()

@app.get("/kpis")
def obtener_kpis(
    year: int = Query(None),
    nsemana: int = Query(None),
    codsalon: int = Query(None)
):
    try:
        data = leer_kpis(year=year, nsemana=nsemana, codsalon=codsalon)
        return {"kpis": data}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "trace": traceback.format_exc()
            }
        )



