import pandas as pd
import requests
from io import StringIO

def leer_kpis(year=None, nsemana=None, codsalon=None, tipo="semana"):
    sheet_id = "1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0"
    gid_map = {
        "semana": "2036398995",
        "trabajadores": "31094205",
        "mensual": "1333792005"
    }

    gid = gid_map.get(tipo)
    if not gid:
        raise ValueError(f"Tipo de hoja desconocido: '{tipo}'")

    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    print(f"🌐 Consultando Google Sheet: {url}")
    
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error al descargar: {response.status_code}")

    df = pd.read_csv(StringIO(response.text))
    df.columns = df.columns.str.lower().str.strip()

    # Aplicar filtros si existen
    if year is not None and 'year' in df.columns:
        df = df[df['year'] == year]
    if nsemana is not None and 'nsemana' in df.columns:
        df = df[df['nsemana'] == nsemana]
    if codsalon is not None and 'codsalon' in df.columns:
        df = df[df['codsalon'] == codsalon]

    print("📊 Columnas:", df.columns.tolist())
    print("📈 Filas tras filtros:", len(df))
    print(df.head())  # Log para revisar los datos

    return df
