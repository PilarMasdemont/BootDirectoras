from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from sheets import leer_kpis
import traceback

app = FastAPI()

@app.get("/kpis")
def obtener_kpis(
    year: int = Query(None, description="Año, por ejemplo 2025"),
    nsemana: int = Query(None, description="Número de semana"),
    codsalon: int = Query(None, description="Código de salón"),
    tipo: str = Query("semana", description="Tipo de hoja: semana, trabajadores, mensual")
):
    try:
        df = leer_kpis(year=year, nsemana=nsemana, codsalon=codsalon, tipo=tipo)
        return {"kpis": df.to_dict(orient="records")}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "trace": traceback.format_exc()}
        )
