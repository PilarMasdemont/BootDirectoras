import pandas as pd

# Configuración de hojas de Google Sheets
URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0/export?format=csv"
HOJAS = {
    "semana": 2036398995,
}

COLUMNAS_UTILES = [
    "year", "nsemana", "codsalon", "facturacionsiva", "ticketmedio", "horasfichadas",
    "ratiogeneral", "ratiodesviaciontiempoteorico", "ratiotiempoindirecto", "ratioticketsinferior20"
]

def leer_kpis(year=None, nsemana=None, codsalon=None, tipo="semana"):
    hoja_id = HOJAS[tipo]
    url = f"{URL_GOOGLE_SHEET}&gid={hoja_id}"
    df = pd.read_csv(url)
    df.columns = [col.lower() for col in df.columns]
    df = df.replace("(en blanco)", pd.NA)

    for col in ["year", "nsemana", "codsalon"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    columnas_utiles = [c for c in df.columns if c in COLUMNAS_UTILES]
    df = df[columnas_utiles]

    if year is not None:
        df = df[df["year"] == year]
    if nsemana is not None:
        df = df[df["nsemana"] == nsemana]
    if codsalon is not None:
        df = df[df["codsalon"] == codsalon]
        print("📦 DataFrame después de filtros:")
        print(df.head())
        print("🔢 Número de filas:", len(df))

    return df

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

    # Cálculos seguros
    ratiogeneral = df["ratiogeneral"].mean()
    impacto_total = df["facturacionsiva"].astype(float).sum()

    # Manejo de valores no válidos para JSON
    if pd.isna(ratiogeneral) or pd.isnull(ratiogeneral) or not pd.api.types.is_number(ratiogeneral):
        ratiogeneral = None

    if pd.isna(impacto_total) or pd.isnull(impacto_total) or not pd.api.types.is_number(impacto_total):
        impacto_total = None

    return {
        "ratiogeneral": ratiogeneral,
        "impacto_total": impacto_total,
        "positivos": [],
        "negativos": [],
        "mejoras": []
    }
