import pandas as pd
import requests
from io import StringIO

# Diccionario con las URLs de los documentos de Google Sheets
GOOGLE_SHEETS = {
    "semana": "https://docs.google.com/spreadsheets/d/1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0/export?format=csv&gid=2036398995",
    "trabajadores": "https://docs.google.com/spreadsheets/d/1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0/export?format=csv&gid=1333321633",
    "mensual": "https://docs.google.com/spreadsheets/d/1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0/export?format=csv&gid=902950106"
}

def leer_kpis(year: int, nsemana: int, codsalon: int, tipo: str = "semana") -> pd.DataFrame:
    """
    Carga datos desde una hoja de Google Sheets según el tipo ('semana', 'trabajadores', 'mensual'),
    y los filtra por año, semana y código de salón.
    """
    url = GOOGLE_SHEETS.get(tipo)
    if not url:
        raise ValueError(f"Tipo de hoja no reconocido: {tipo}")

    print(f"🌐 Consultando Google Sheet: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error al obtener datos: {response.status_code}")

    df = pd.read_csv(StringIO(response.text))

    print("📊 Columnas:", list(df.columns))

    # Normalizar nombres de columnas si es necesario (opcional)
    df.columns = df.columns.str.strip().str.lower()

    # Convertimos codsalon a numérico (filtrando errores como '(en blanco)')
    if "codsalon" in df.columns:
        df["codsalon"] = pd.to_numeric(df["codsalon"], errors="coerce")
    if "nsemana" in df.columns:
        df["nsemana"] = pd.to_numeric(df["nsemana"], errors="coerce")
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")

    df = df.dropna(subset=["codsalon", "nsemana", "year"])
    df = df.astype({"codsalon": int, "nsemana": int, "year": int})

    df_filtrado = df[
        (df["year"] == year) &
        (df["nsemana"] == nsemana) &
        (df["codsalon"] == codsalon)
    ]

    print(f"📈 Filas tras filtros: {len(df_filtrado)}")
    return df_filtrado

