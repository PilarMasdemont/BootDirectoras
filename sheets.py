import pandas as pd
import requests
from io import StringIO
import numpy as np

def leer_kpis(year: int = None, nsemana: int = None, codsalon: int = None):
    sheet_id = "1-40eCYIUj8yKBC1w55ukAO45lLnL7gEm1-p_OLkL8Lk"
    gid = "1076160199"
    SHEET_URL = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    response = requests.get(SHEET_URL)
    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code}: {response.reason}")

    df = pd.read_csv(StringIO(response.text))

    # Normaliza nombres de columnas
    df.columns = df.columns.str.strip().str.lower()

    # Convierte columnas relevantes a numérico, ignora errores
    columnas_numericas = ["year", "nsemana", "codsalon"]
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            raise KeyError(f"Columna esperada no encontrada: '{col}'")

    # Filtro por parámetros si se han proporcionado
    if year is not None:
        df = df[df['year'] == year]
    if nsemana is not None:
        df = df[df['nsemana'] == nsemana]
    if codsalon is not None:
        df = df[df['codsalon'] == codsalon]

    # Reemplaza valores inválidos en JSON
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna("null", inplace=True)

    return df.to_dict(orient="records")





