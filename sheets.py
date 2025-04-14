import pandas as pd
import requests
from io import StringIO
import numpy as np

def leer_kpis(year=None, nsemana=None, codsalon=None):
    sheet_id = "1-40eCYIUj8yKBC1w55ukAO45lLnL7gEm1-p_OLkL8Lk"
    gid = "1076160199"
    SHEET_URL = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    response = requests.get(SHEET_URL)
    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code}: {response.reason}")

    df = pd.read_csv(StringIO(response.text))

    # 🔧 Limpiar y normalizar nombres de columnas
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "")
        .str.replace("\ufeff", "")  # BOM character a veces presente
    )

    # Mostrar columnas para depuración
    columnas_actuales = list(df.columns)

    # ✅ Asegurarse de que las columnas que queremos filtrar existan
    for col in ['year', 'nsemana', 'codsalon']:
        if col not in df.columns:
            raise KeyError(f"Columna esperada no encontrada: '{col}'. Columnas disponibles: {columnas_actuales}")

    # Convertir columnas a numéricas
    for col in ['year', 'nsemana', 'codsalon']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Filtrar según parámetros si están presentes
    if year is not None:
        df = df[df['year'] == int(year)]
    if nsemana is not None:
        df = df[df['nsemana'] == int(nsemana)]
    if codsalon is not None:
        df = df[df['codsalon'] == int(codsalon)]

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna("null", inplace=True)

    return df.to_dict(orient="records")






