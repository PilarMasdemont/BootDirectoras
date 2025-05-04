# funciones/analizar_salon.py
from funciones.base import leer_kpis

def analizar_salon(year: int, nsemana: int, codsalon: int, tipo: str = "semana") -> str:
    df = leer_kpis(year, nsemana, codsalon, tipo)
    if df.empty:
        return "No hay datos para analizar el salón."
    kpis = [c for c in df.columns if c not in ['año', 'nsemana', 'cod_salon']]
    respuesta = "📊 Análisis del salón:\n"
    for kpi in kpis:
        valor = df[kpi].mean()
        respuesta += f"- {kpi}: {valor:.2f}\n"
    return respuesta
