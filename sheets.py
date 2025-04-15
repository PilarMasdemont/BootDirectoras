import pandas as pd
import requests
from io import StringIO
import numpy as np

def leer_kpis(year=None, nsemana=None, codsalon=None):
    # ✅ Hoja: KPIsSemanaS (simplificada)
    sheet_id = "1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0"
    gid = "2099980865"  # Hoja específica

    SHEET_URL = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    response = requests.get(SHEET_URL)
    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code}: {response.reason}")

    csv_text = response.text

    # 🔍 Intentar leer con separador ';' (por configuración regional Excel)
    try:
        df = pd.read_csv(StringIO(csv_text), sep=';')
        if df.shape[1] == 1:
            # Si sólo hay una columna, probar con separador ','
            df = pd.read_csv(StringIO(csv_text), sep=',')
    except Exception as e:
        raise Exception(f"Error al leer el CSV: {e}")

    # 🔧 Limpiar nombres de columnas
    df.columns = df.columns.str.strip().str.lower()

    print("🔎 Columnas detectadas:", df.columns.tolist())  # 👈 Para depuración en logs

    columnas_requeridas = ['year', 'nsemana', 'codsalon']
    for col in columnas_requeridas:
        if col not in df.columns:
            raise KeyError(f"Columna esperada no encontrada: '{col}'. Columnas disponibles: {df.columns.tolist()}")

    # 🔢 Conversión de tipos
    for col in columnas_requeridas:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 🔍 Filtros
    if year is not None:
        df = df[df['year'] == year]
    if nsemana is not None:
        df = df[df['nsemana'] == nsemana]
    if codsalon is not None:
        df = df[df['codsalon'] == codsalon]

    # ✅ Limpiar valores no válidos
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df = df.where(pd.notnull(df), None)

    return df.to_dict(orient="records")
