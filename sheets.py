import pandas as pd
import requests
from io import StringIO
import numpy as np

def leer_kpis(year=None, nsemana=None, codsalon=None, tipo="semana"):
    # ID general del documento
    sheet_id = "1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0"
    
    # Diccionario de tipos con sus respectivos GIDs
    gid_map = {
        "semana": "2036398995",       # KPIs por semana y salón
        "trabajadores": "31094205",   # KPIs por semana y trabajador
        "mensual": "1333792005"       # KPIs mensuales por salón
    }

    if tipo not in gid_map:
        raise ValueError(f"Tipo de hoja desconocido: '{tipo}'")

    gid = gid_map[tipo]
    SHEET_URL = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    print(f"🌐 Consultando Google Sheet ({tipo}): {SHEET_URL}")

    response = requests.get(SHEET_URL)
    print(f"📥 Estado de la respuesta: {response.status_code}")

    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code}: {response.reason}")

    csv_text = response.text
    df = pd.read_csv(StringIO(csv_text), sep=",")
    df.columns = df.columns.str.strip().str.lower()
    print("🔎 Columnas detectadas:", df.columns.tolist())

    # Filtros dinámicos según columnas presentes
    columnas_filtro = [col for col in ['year', 'nsemana', 'codsalon'] if col in df.columns]
    for col in columnas_filtro:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    if year is not None and 'year' in df.columns:
        df = df[df['year'] == year]
    if nsemana is not None and 'nsemana' in df.columns:
        df = df[df['nsemana'] == nsemana]
    if codsalon is not None and 'codsalon' in df.columns:
        df = df[df['codsalon'] == codsalon]

    print(f"📊 Filas tras aplicar filtros: {len(df)}")

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df = df.where(pd.notnull(df), None)

    return df.to_dict(orient="records")
