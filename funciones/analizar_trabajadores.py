# funciones/analizar_trabajadores.py
from funciones.base import leer_kpis

def analizar_trabajadores(year: int, nsemana: int, codsalon: int, tipo: str = "trabajadores") -> str:
    df = leer_kpis(year, nsemana, codsalon, tipo)
    if 'trabajador' not in df.columns:
        return "La tabla no contiene datos por trabajador."
    agrupado = df.groupby('trabajador').mean(numeric_only=True)
    return "👥 Análisis por trabajador:\n" + agrupado.to_string()
