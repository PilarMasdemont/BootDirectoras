from fastapi import FastAPI
from sheets import leer_kpis
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/kpis")
def obtener_kpis():
    try:
        data = leer_kpis()
        return {"kpis": data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
