import pandas as pd
import requests
from io import StringIO
import numpy as np

def leer_kpis(year=None, nsemana=None, codsalon=None):
    # ✅ Datos de la hoja
    sheet_id = "1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0"
    gid = "2036398995"  # Hoja "KPIsSemanaS"

    SHEET_URL = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    print(f"🌐 Consultando Google Sheet: {SHEET_URL}")

    response = requests.get(SHEET_URL)
    print(f"📥 Estado de la respuesta: {response.status_code}")

    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code}: {response.reason}")

    csv_text = response.text
    df = pd.read_csv(StringIO(csv_text), sep=",")
    df.columns = df.columns.str.strip().str.lower()
    print("🔎 Columnas detectadas:", df.columns.tolist())

    columnas_requeridas = ['year', 'nsemana', 'codsalon']
    for col in columnas_requeridas:
        if col not in df.columns:
            raise KeyError(f"❌ Columna esperada no encontrada: '{col}'. Columnas disponibles: {df.columns.tolist()}")

    # Conversión a numérico
    for col in columnas_requeridas:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Filtros
    print(f"🔍 Filtros aplicados - year: {year}, nsemana: {nsemana}, codsalon: {codsalon}")
    if year is not None:
        df = df[df['year'] == year]
    if nsemana is not None:
        df = df[df['nsemana'] == nsemana]
    if codsalon is not None:
        df = df[df['codsalon'] == codsalon]

    print(f"📊 Filas tras aplicar filtros: {len(df)}")

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df = df.where(pd.notnull(df), None)

    return df.to_dict(orient="records")
