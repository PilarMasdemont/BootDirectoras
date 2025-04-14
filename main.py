from fastapi import FastAPI, Query
from sheets import leer_kpis
from fastapi.responses import JSONResponse
import traceback

app = FastAPI()

@app.get("/kpis")
def obtener_kpis(semana: int = Query(None), codsalon: int = Query(None)):
    try:
        data = leer_kpis()

        # Asegurarse de que los datos están cargados como lista
        if not isinstance(data, list):
            return JSONResponse(
                status_code=500,
                content={"error": "Los datos no se cargaron correctamente"}
            )

        if semana is not None:
            data = [kpi for kpi in data if str(kpi.get("semana")).strip() == str(semana)]
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

