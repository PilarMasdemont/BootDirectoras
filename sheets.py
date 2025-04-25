from pathlib import Path

# Código corregido con mejoras en la limpieza y conversión de datos
sheets_code = """
import pandas as pd

URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0/export?format=csv"
HOJAS = {
    "semana": 2036398995,
    "trabajadores": 1059972214,
    "mensual": 953186733,
}

COLUMNAS_UTILES = [
    "year", "nsemana", "codsalon", "facturacionsiva", "ticketmedio", "horasfichadas",
    "ratiogeneral", "ratiodesviaciontiempoteorico", "ratiotiempoindirecto", "ratioticketsinferior20"
]

def leer_kpis(year=None, nsemana=None, codsalon=None, tipo="semana"):
    hoja_id = HOJAS[tipo]
    url = f"{URL_GOOGLE_SHEET}&gid={hoja_id}"
    print(f"🌐 Consultando Google Sheet: {url}")
    df = pd.read_csv(url)

    # Normaliza nombres de columnas
    df.columns = [col.lower().strip().replace(" ", "_") for col in df.columns]

    # Limpieza básica
    df = df.replace(["(en blanco)", "", "NA", "n/a"], pd.NA)

    # Conversión robusta de columnas numéricas
    for col in df.columns:
        if col in COLUMNAS_UTILES:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", ".", regex=False)
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Filtrado por columnas útiles
    df = df[[c for c in df.columns if c in COLUMNAS_UTILES]]

    # Aplicar filtros
    if year is not None:
        df = df[df["year"] == year]
    if nsemana is not None:
        df = df[df["nsemana"] == nsemana]
    if codsalon is not None:
        df = df[df["codsalon"] == codsalon]

    print(f"📦 DataFrame después de filtros (filas: {len(df)}):")
    print(df.head())

    return df.dropna(how="any")

def analizar_salon(df):
    if df.empty:
        return {
            "ratiogeneral": None,
            "impacto_total": None,
            "positivos": [],
            "negativos": [],
            "mejoras": [],
            "error": "No hay datos"
        }

    df = df.apply(pd.to_numeric, errors="coerce").dropna()

    ratiogeneral = df["ratiogeneral"].mean()
    impacto_total = df["facturacionsiva"].sum()

    return {
        "ratiogeneral": ratiogeneral,
        "impacto_total": impacto_total,
        "positivos": [],
        "negativos": [],
        "mejoras": []
    }
"""

output_path.name
