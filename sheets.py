import pandas as pd
import requests
from io import StringIO
import numpy as np

def leer_kpis(year=None, nsemana=None, codsalon=None):
    # 🔗 HOJA TEST para validar formato limpio
    sheet_id = "1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0"
    gid = "1830919141"  # <-- ID de la hoja 'TEST_KPIsSemanaS'

    SHEET_URL = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    response = requests.get(SHEET_URL)
    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code}: {response.reason}")

    # Leer y convertir decimal
    csv_text = response.text.replace(",", ".")
    df = pd.read_csv(StringIO(csv_text))

    # Limpieza de columnas
    df.columns = df.columns.str.strip().str.lower()
    print("🔎 Columnas detectadas:", df.columns.tolist())

    columnas_requeridas = ['year', 'nsemana', 'codsalon']
    for col in columnas_requeridas:
        if col not in df.columns:
            raise KeyError(f"Columna esperada no encontrada: '{col}'. Columnas disponibles: {df.columns.tolist()}")

    for col in columnas_requeridas:
        df[col] = pd.to_numeric(df[col], errors='coerce_

