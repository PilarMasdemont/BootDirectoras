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
    print(f"🌐 Consultando Google Sheet: {url}")
    df = pd.read_csv(url)
    
    df.columns = [col.lower() for col in df.columns]
    print(f"📄 Columnas leídas: {df.columns.tolist()}")
    
    df = df.replace("(en blanco)", pd.NA)

    # Reemplazar comas por puntos en TODAS las columnas
    df = df.apply(lambda x: x.astype(str).str.replace(",", ".", regex=False))

    # Convertir columnas específicas a valores numéricos
    for col in ["year", "nsemana", "codsalon"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    columnas_utiles = [c for c in df.columns if c in COLUMNAS_UTILES]
    df = df[columnas_utiles]
    
    # Filtros
    print(f"🔎 Filtros aplicados: year={year}, nsemana={nsemana}, codsalon={codsalon}")
    if year is not None:
        df = df[df["year"] == year]
    if nsemana is not None:
        df = df[df["nsemana"] == nsemana]
    if codsalon is not None:
        df = df[df["codsalon"] == codsalon]

    print(f"📦 DataFrame después de filtros (filas: {len(df)}):")
    print(df.head())
    return df

def analizar_salon(df):
    if df.empty:
        return {
            "ratiogeneral": None, 
            "impacto_total": 0.0,
            "positivos": [], 
            "negativos": [], 
            "mejoras": [], 
            "error": "No hay datos"
        }

    df = df.apply(pd.to_numeric, errors="coerce").dropna()

    ratiogeneral = df["ratiogeneral"].mean()
    impacto_total = df["facturacionsiva"].astype(float).sum()

    return {
        "ratiogeneral": ratiogeneral,
        "impacto_total": impacto_total,
        "positivos": [],
        "negativos": [],
        "mejoras": []
    }

