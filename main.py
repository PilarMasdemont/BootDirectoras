from fastapi import FastAPI
from sheets import leer_kpis

app = FastAPI()

@app.get("/kpis")
def obtener_kpis():
    return leer_kpis()
