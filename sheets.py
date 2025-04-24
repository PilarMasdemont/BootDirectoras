
import pandas as pd

# URLs y configuración de hojas de Google Sheets
URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0/export?format=csv"
HOJAS = {
    "semana": 2036398995,
    "trabajadores": 1059972214,
    "mensual": 953186733,
}

# Columnas que se utilizarán
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

    print(f"📊 Columnas: {df.columns.tolist()}")
    print(f"📈 Filas tras filtros: {len(df)}")
    return df


# 🚀 Nueva función de análisis por salón
def analizar_salon(df):
    if df.empty:
        return {
            "ratiogeneral": None,
            "impacto_total": None,
            "positivos": [],
            "negativos": [],
            "mejoras": [],
            "error": "No hay datos para analizar"
        }

    ratiogeneral = pd.to_numeric(df["ratiogeneral"], errors="coerce").mean()

    positivos = []
    negativos = []
    mejoras = []

    if ratiogeneral > 1.8:
        positivos.append("Buen ratio general")
    elif ratiogeneral < 1.3:
        negativos.append("Ratio general bajo")
    else:
        mejoras.append("Ratio general en zona de mejora")

    return {
        "ratiogeneral": round(ratiogeneral, 2),
        "impacto_total": round(ratiogeneral, 2),
        "positivos": positivos,
        "negativos": negativos,
        "mejoras": mejoras
    }
