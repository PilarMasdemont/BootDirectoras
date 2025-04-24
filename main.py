@app.get("/kpis")
def obtener_kpis(
    year: int = Query(None),
    nsemana: int = Query(None),
    codsalon: int = Query(None),
    tipo: str = Query("semana")
):
    try:
        data = leer_kpis(year=year, nsemana=nsemana, codsalon=codsalon, tipo=tipo)
        return {"kpis": data.to_dict(orient="records")}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


