import pandas as pd
from sheets import cargar_hoja

def explicar_ratio_semanal(codsalon: str, nsemana: int, year: int) -> str:
    try:
        df = cargar_hoja("72617950")  # GID de la hoja semanal
    except Exception as e:
        return f"⚠️ Error al cargar datos desde Google Sheets: {e}"

    columnas_utiles = [
        "year", "nsemana", "codsalon", "facturacionsiva", "horasfichadas",
        "ratiogeneral", "ratiodesviaciontiempoteorico", "ratiotiempoindirecto",
        "ratioticketsinferior20", "n_ticketsiva", "ticketsivamedio"
    ]

    faltantes = [col for col in columnas_utiles if col not in df.columns]
    if faltantes:
        return f"⚠️ Faltan columnas necesarias en los datos: {', '.join(faltantes)}"

    df = df[df["codsalon"].astype(str) == str(codsalon)]
    df = df[(df["nsemana"] == nsemana) & (df["year"] == year)]

    if df.empty:
        return f"⚠️ No se encontraron datos para el salón {codsalon} en la semana {nsemana} del año {year}."

    fila = df.iloc[0]
    ratio = fila.get("ratiogeneral", None)

    if ratio is None or pd.isna(ratio):
        return "⚠️ No se encuentra el valor del Ratio General para esa semana."

    explicacion = f"El Ratio General fue {ratio:.2f} en la semana {nsemana} del año {year}.\n"

    if fila["ratiodesviaciontiempoteorico"] > 1:
        explicacion += "Hubo desviación en el tiempo teórico previsto.\n"
    if fila["ratiotiempoindirecto"] > 0.2:
        explicacion += "El tiempo indirecto fue elevado.\n"
    if fila["ratioticketsinferior20"] > 0.3:
        explicacion += "Muchos tickets fueron inferiores a 20€.\n"

    return explicacion.strip()
