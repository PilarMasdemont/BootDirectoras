"""
Explica por qué el Ratio General fue alto, medio o bajo en un día concreto para un salón,
basándose en otros KPIs diarios de la hoja 'KPIs_30Dias'.
"""

import pandas as pd
from datetime import datetime
from sheets import cargar_hoja

GID_KPIS_30DIAS = "1882861530"

def explicar_ratio_diario(codsalon: str, fecha: str) -> str:
    # Cargar los datos de la hoja
    df = cargar_hoja(gid=GID_KPIS_30DIAS)

    # Asegurar que la columna fecha esté en formato datetime.date
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce").dt.date
    fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()

    # Filtrar por salón y fecha
    fila = df[
        (df["codsalon"].astype(str) == codsalon) &
        (df["fecha"] == fecha_dt)
    ]

    if fila.empty:
        return f"No se encontraron datos para el salón {codsalon} el día {fecha}."

    fila = fila.iloc[0]

    # Convertir ratio a porcentaje
    ratio = float(fila["ratiogeneral"]) * 100
    desviacion = float(fila["ratiodesviaciontiempoteorico"])
    tiempo_indirecto = float(fila["ratiotiempoindirecto"])
    tickets_bajos = float(fila["ratioticketsinferior20"])

    # Clasificación
    if ratio >= 200:
        calificacion = "excelente"
    elif ratio >= 130:
        calificacion = "aceptable"
    else:
        calificacion = "bajo"

    causas = []

    if tickets_bajos > 40:
        causas.append(f"un {tickets_bajos:.0f}% de tickets inferiores a 20 €")
    if tiempo_indirecto > 20:
        causas.append(f"{tiempo_indirecto:.0f}% de tiempo indirecto")
    if desviacion < 0:
        causas.append(f"una desviación negativa de la agenda de {desviacion:.1f}%")

    if causas:
        resumen = "Esto se debe principalmente a " + ", ".join(causas[:-1])
        if len(causas) > 1:
            resumen += " y " + causas[-1]
        else:
            resumen = "Esto se debe principalmente a " + causas[0]
        resumen += "."
    else:
        resumen = "No se detectan causas claras en los indicadores asociados."

    return (
        f"📅 El {fecha}, el Ratio General del salón fue del {ratio:.0f}%, lo que se considera {calificacion}. "
        + resumen
    )
