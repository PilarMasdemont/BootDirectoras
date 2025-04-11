from fastapi import FastAPI
from sheets import leer_kpis
from fastapi.responses import JSONResponse
import traceback  # <--- Añade esto

app = FastAPI()

@app.get("/kpis")
def obtener_kpis():
    try:
        data = leer_kpis()
        return {"kpis": data}
    except Exception as e:
        # Devuelve también la traza completa del error
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "trace": traceback.format_exc()
            }
        )

