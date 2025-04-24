from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from sheets import leer_kpis
import traceback

app = FastAPI()

@app.get("/kpis")
def obtener_datos_crudos(
    year: int = Query(...),
    nsemana: int = Query(...),
    codsalon: int = Query(...),
    tipo: str = Query("semana")
):
    try:
        df = leer_kpis(year=year, nsemana=nsemana, codsalon=codsalon, tipo=tipo)
        return {"filas": len(df), "datos": df.to_dict(orient="records")}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "trace": traceback.format_exc()
            }
        )
