import pandas as pd
import requests
from io import StringIO
import numpy as np

def leer_kpis(year=None, nsemana=None, codsalon=None):
    sheet_id = "1-40eCYIUj8yKBC1w55ukAO45lLnL7gEm1-p_OLkL8Lk"
    gid = "1801451782"  # <-- KPIsSemanaS

    SHEET_URL = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    response = requests.get(SHEET_URL)
    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code}: {response.reason}")

    # Lee como texto y cambia ',' por '.' para los decimales
    csv_text = response.text.replace(",", ".")
    df = pd.read_csv(StringIO(csv_text))

    # Limpieza de nombres de columna
    df.columns = df.columns.str.strip().str.lower()

    # Convertir columnas clave a numérico (asegurarse)
    for col in ['year', 'nsemana', 'codsalon']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Aplicar filtros si se pasan
    if year is not None:
        df = df[df['year'] == year]
    if nsemana is not None:
        df = df[df['nsemana'] == nsemana]
    if codsalon is not None:
        df = df[df['codsalon'] == codsalon]

    # Limpiar para ser JSON-compatible
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df = df.where(pd.notnull(df), None)

    return df.to_dict(orient="records")



