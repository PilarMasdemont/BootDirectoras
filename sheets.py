import pandas as pd
import requests
from io import StringIO
import numpy as np

def leer_kpis(year=None, nsemana=None, codsalon=None):
    sheet_id = "1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0"
    gid = "2099980865"  # ✅ KPIsSemanaS (con year, nsemana, codsalon)

    SHEET_URL = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    response = requests.get(SHEET_URL)
    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code}: {response.reason}")

    # Ajustar formato decimal
    csv_text = response.text.replace(",", ".")
    df = pd.read_csv(StringIO(csv_text))

    # Limpiar nombres de columnas
    df.columns = df.columns.str.strip().str.lower()

    # Convertir columnas clave a número
    for col in ['year', 'nsemana', 'codsalon']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Filtrar si hay parámetros
    if year is not None:
        df = df[df['year'] == year]
    if nsemana is not None:
        df = df[df['nsemana'] == nsemana]
    if codsalon is not None:
        df = df[df['codsalon'] == codsalon]

    # Para que sea compatible con JSON
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df = df.where(pd.notnull(df), None)

    return df.to_dict(orient="records")


