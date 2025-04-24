# Creamos el contenido completo del archivo main.py ajustado
main_py_code = '''
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from sheets import leer_kpis, analizar_trabajadores, analizar_salon, safe_json
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
        data = leer_kpis(year=year, nsemana=nsemana, codsalon=codsalon, tipo=tipo)
        return {"kpis": data.to_dict(orient="records")}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "trace": traceback.format_exc()}
        )

@app.get("/kpis/trabajadores/analisis")
def analisis_trabajadores(
    year: int = Query(...),
    nsemana: int = Query(...),
    codsalon: int = Query(...)
):
    try:
        df = leer_kpis(year=year, nsemana=nsemana, codsalon=codsalon, tipo="trabajadores")
        resultado = analizar_trabajadores(df)
        return {"analisis": safe_json(resultado)}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "trace": traceback.format_exc()}
        )

@app.get("/kpis/salon/analisis")
def analisis_salon(
    year: int = Query(...),
    nsemana: int = Query(...),
    codsalon: int = Query(...)
):
    try:
        df = leer_kpis(year=year, nsemana=nsemana, codsalon=codsalon, tipo="semana")
        resultado = analizar_salon(df)
        return {"analisis": safe_json(resultado)}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "trace": traceback.format_exc()}
        )
'''

# Guardamos el archivo main.py actualizado
main_file_path = "/mnt/data/main_actualizado.py"
with open(main_file_path, "w", encoding="utf-8") as f:
    f.write(main_py_code)

main_file_path
