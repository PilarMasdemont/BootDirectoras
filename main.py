from fastapi import FastAPI, Query
from sheets import leer_kpis
from fastapi.responses import JSONResponse
import traceback

app = FastAPI()

@app.get("/kpis")
def obtener_kpis(
    year: int = Query(...),
    semana: int = Query(...),
    codsalon: int = Query(...)
):
    try:
        data = leer_kpis()

        if not isinstance(data, list):
            return JSONResponse(
                status_code=500,
                content={"error": "Los datos no se cargaron correctamente"}
            )

        # Filtrado
        filtered = [
            kpi for kpi in data
            if str(kpi.get("year")).strip() == str(year)
            and str(kpi.get("semana")).strip() == str(semana)
            and int(kpi.get("codsalon", -1)) == codsalon
        ]

        return {"kpis": filtered}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "trace": traceback.format_exc()
            }
        )

