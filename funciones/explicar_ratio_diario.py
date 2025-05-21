import httpx
import pandas as pd
from sheets import cargar_hoja


def explicar_ratio_diario(codsalon: str, fecha: str) -> str:
    try:
        df = cargar_hoja("1882861530")
    except Exception as e:
        return f"⚠️ Error al cargar datos desde Google Sheets: {e}"

    columnas_utiles = [
        "year", "fecha", "codsalon", "facturacionsiva", "horasfichadas",
        "ratiogeneral", "ratiodesviaciontiempoteorico", "ratiotiempoindirecto",
        "ratioticketsinferior20", "ticketsivamedio", "n_ticketsiva"
    ]

    faltantes = [col for col in columnas_utiles if col not in df.columns]
    if faltantes:
        return f"⚠️ Faltan columnas necesarias en los datos: {', '.join(faltantes)}"

    df = df[df["codsalon"].astype(str) == str(codsalon)]
    df = df[df["fecha"] == fecha]

    if df.empty:
        return f"⚠️ No se encontraron datos para el salón {codsalon} en la fecha {fecha}."

    fila = df.iloc[0]
    ratio = fila.get("ratiogeneral", None)

    if ratio is None or pd.isna(ratio):
        return "⚠️ No se encuentra el valor del Ratio General para esa fecha."

    explicacion = f"El Ratio General fue {ratio:.2f} el día {fecha}.\n"

    if fila["ratiodesviaciontiempoteorico"] > 1:
        explicacion += "Hubo desviación en el tiempo teórico previsto.\n"
    if fila["ratiotiempoindirecto"] > 0.2:
        explicacion += "El tiempo indirecto fue elevado.\n"
    if fila["ratioticketsinferior20"] > 0.3:
        explicacion += "Muchos tickets fueron inferiores a 20€.\n"

    return explicacion.strip()


# Endpoint opcional para depurar columnas disponibles en la hoja de cálculo
from fastapi import APIRouter
router = APIRouter()

@router.get("/debug/columnas")
def columnas_disponibles():
    try:
        df = cargar_hoja("1882861530")
        return {"columnas": list(df.columns)}
    except Exception as e:
        return {"error": str(e)}

