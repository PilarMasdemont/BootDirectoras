# funciones/explicar_variacion.py
from funciones.base import leer_kpis

def explicar_variacion(year: int, nsemana: int, codsalon: int, tipo: str = "semana") -> str:
    df_actual = leer_kpis(year, nsemana, codsalon, tipo)
    df_anterior = leer_kpis(year, nsemana - 1, codsalon, tipo)

    if df_actual.empty or df_anterior.empty:
        return "No hay suficientes datos para comparar semanas."

    comparables = set(df_actual.columns) & set(df_anterior.columns)
    mensaje = "📈 Variación respecto a la semana anterior:\n"

    for col in comparables:
        if col in ['año', 'nsemana', 'cod_salon']:
            continue
        act = df_actual[col].mean()
        ant = df_anterior[col].mean()
        diff = act - ant
        pct = (diff / ant * 100) if ant != 0 else 0
        mensaje += f"- {col}: {act:.2f} ({pct:+.1f}% vs semana anterior)\n"

    return mensaje
