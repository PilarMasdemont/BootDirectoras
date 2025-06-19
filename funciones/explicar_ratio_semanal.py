import pandas as pd
from sheets import cargar_hoja

def explicar_ratio_semanal(codsalon: str, nsemana: int) -> str:
    try:
        df = cargar_hoja("72617950")  # GID de la hoja semanal
    except Exception as e:
        return f"⚠️ Error al cargar datos: {e}"

    columnas_requeridas = [
        "year", "nsemana", "codsalon", "facturacionsiva", "horasfichadas",
        "ratiogeneral", "ratiodesviaciontiempoteorico", "ratiotiempoindirecto",
        "ratioticketsinferior20", "n_ticketsiva", "ticketsivamedio"
    ]
    if any(col not in df.columns for col in columnas_requeridas):
        return "⚠️ La hoja de datos no contiene todas las columnas necesarias."

    df["codsalon"] = df["codsalon"].astype(str)
    datos = df[(df["codsalon"] == codsalon) & (df["nsemana"] == nsemana)]

    if datos.empty:
        return f"⚠️ No se encontraron datos para el salón {codsalon} en la semana {nsemana}."

    fila = datos.iloc[0]
    ratio = fila["ratiogeneral"]

    resumen = [f"El ratio general en la semana {nsemana} fue {ratio:.2f}."]

    if fila["ratiodesviaciontiempoteorico"] > 1:
        resumen.append("Hubo una desviación significativa entre el tiempo agendado y el trabajado.")
    if fila["ratiotiempoindirecto"] > 0.2:
        resumen.append("El tiempo indirecto fue elevado, lo que indica menor productividad.")
    if fila["ratioticketsinferior20"] > 0.3:
        resumen.append("Una proporción alta de tickets fueron inferiores a 20 €, lo que afecta la rentabilidad.")
    if fila["facturacionsiva"] < 1000:
        resumen.append("La facturación fue baja para lo esperado en una semana estándar.")

    return "\n".join(resumen)
