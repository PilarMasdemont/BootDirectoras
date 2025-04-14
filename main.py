from fastapi import FastAPI, Query
from sheets import leer_kpis
from fastapi.responses import JSONResponse
import traceback

app = FastAPI()

@app.get("/kpis")
def obtener_kpis(fecha: str = Query(None), codsalon: int = Query(None)):
    try:
        data = leer_kpis()

        # Filtro por fecha si se proporciona
        if fecha:
            data = [kpi for kpi in data if kpi.get("fecha", "").startswith(fecha)]

        # Filtro por codsalon si se proporciona
        if codsalon is not None:
            data = [kpi for kpi in data if int(kpi.get("codsalon", -1)) == codsalon]

        return {"kpis": data}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "trace": traceback.format_exc()
            }
        )
