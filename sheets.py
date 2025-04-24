import pandas as pd

URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0/export?format=csv"
HOJAS = {"semana": 2036398995}

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
    
    df = df[[c for c in df.columns if c in COLUMNAS_UTILES]]
    
    if year: df = df[df["year"] == year]
    if nsemana: df = df[df["nsemana"] == nsemana]
    if codsalon: df = df[df["codsalon"] == codsalon]
    
    return df.dropna()

def explicar_kpi(nombre_kpi):
    explicaciones = {
        "ratiogeneral": "Mide la facturación por hora trabajada.",
        "ticketmedio": "Promedio de facturación por ticket.",
        "horasfichadas": "Horas que han sido registradas por el personal.",
        "ratioticketsinferior20": "Proporción de tickets con importe menor a 20€.",
        # Puedes ampliar aquí...
    }
    return explicaciones.get(nombre_kpi.lower(), "No tengo una explicación aún para este KPI.")

def analizar_salon(df):
    if df.empty:
        return {"ratiogeneral": None, "impacto_total": None, "error": "No hay datos"}
    
    ratiogeneral = df["ratiogeneral"].mean()
    impacto_total = df["facturacionsiva"].sum()

    return {"ratiogeneral": ratiogeneral, "impacto_total": impacto_total}

def explicar_variacion(df_actual, df_anterior):
    try:
        variacion = df_actual["ratiogeneral"].mean() - df_anterior["ratiogeneral"].mean()
        return {
            "variacion": variacion,
            "interpretacion": "El ratio general ha " + ("subido" if variacion > 0 else "bajado") + f" en {variacion:.2f} puntos."
        }
    except Exception:
        return {"error": "No se pudo calcular la variación entre semanas."}

def analizar_trabajadores(df):
    if "codempleado" not in df.columns:
        return {"error": "No hay datos por trabajador."}
    
    resumen = df.groupby("codempleado").agg({
        "facturacionsiva": "sum",
        "ratiogeneral": "mean",
        "horasfichadas": "sum"
    }).reset_index()

    return resumen.to_dict(orient="records")

def sugerencias_mejora(df):
    sugerencias = []

    if df["ratiotiempoindirecto"].mean() > 0.3:
        sugerencias.append("Reducir el tiempo indirecto por debajo del 30%.")
    
    if df["ratioticketsinferior20"].mean() > 0.25:
        sugerencias.append("Mejorar la estrategia de upselling para tickets bajos.")

    return {"mejoras": sugerencias}
