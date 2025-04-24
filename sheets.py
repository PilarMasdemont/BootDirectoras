import pandas as pd
import requests
import json
from io import StringIO

# URL de los distintos tipos de hojas
URLS = {
    "semana": "https://docs.google.com/spreadsheets/d/1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0/export?format=csv&gid=2036398995",
    "trabajadores": "https://docs.google.com/spreadsheets/d/1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0/export?format=csv&gid=2131808853",
    "mensual": "https://docs.google.com/spreadsheets/d/1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0/export?format=csv&gid=1281961409"
}

def safe_json(obj):
    try:
        return json.loads(json.dumps(obj, allow_nan=False))
    except (ValueError, TypeError) as e:
        return {"error": str(e)}

def leer_kpis(year=None, nsemana=None, codsalon=None, tipo="semana"):
    url = URLS[tipo]
    print(f"\U0001F310 Consultando Google Sheet: {url}")
    resp = requests.get(url)
    print(f"\U0001F4CA Columnas: {resp.status_code}")

    df = pd.read_csv(StringIO(resp.text))

    # Reemplazar ',' por '.' para columnas numéricas
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.replace(',', '.', regex=False)

    # Eliminar filas con valores faltantes en las columnas clave
    df = df.dropna(subset=["year", "nsemana", "codsalon"])

    # Convertir tipos
    df["year"] = df["year"].astype(int)
    df["nsemana"] = df["nsemana"].astype(int)
    df["codsalon"] = df["codsalon"].astype(int)

    if year is not None:
        df = df[df["year"] == year]
    if nsemana is not None:
        df = df[df["nsemana"] == nsemana]
    if codsalon is not None:
        df = df[df["codsalon"] == codsalon]

    print(f"\U0001F4C8 Filas tras filtros: {len(df)}")
    return df

def analizar_salon(df):
    resultado = {
        "ratiogeneral": None,
        "impacto_total": None,
        "positivos": [],
        "negativos": [],
        "mejoras": []
    }
    try:
        df = df.copy()
        df = df.apply(pd.to_numeric, errors='coerce')  # asegúrate de que todo es numérico
        resultado["ratiogeneral"] = df["ratiogeneral"].mean()
    except Exception as e:
        resultado["error"] = str(e)
    return resultado

