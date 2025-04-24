from pathlib import Path

# Crear el contenido corregido para el archivo sheets.py nuevamente (después del reset)
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
    df.columns = [col.lower() for col in df.columns]
    df = df.replace("(en blanco)", pd.NA)

    # Convertir columnas a valores numéricos con errores tolerados
    for col in ["year", "nsemana", "codsalon"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    columnas_utiles = [c for c in df.columns if c in COLUMNAS_UTILES]
    df = df[columnas_utiles]

    # Aplicar filtros
    if year is not None:
        df = df[df["year"] == year]
    if nsemana is not None:
        df = df[df["nsemana"] == nsemana]
    if codsalon is not None:
        df = df[df["codsalon"] == codsalon]

    print(f"📊 Columnas: {df.columns.tolist()}")
    print(f"📈 Filas tras filtros: {len(df)}")
    return df
"""

# Guardar el archivo
path = Path("/mnt/data/sheets.py")
path.write_text(sheets_code)

path.name

