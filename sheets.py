import pandas as pd

URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0/export?format=csv"
HOJAS = {
   # HOJAS SIMPLIFICADAS
HOJAS = {
    "semana": 1549951584,               # KPIs_3Semanas
    "trabajadores": 542959813,          # KPIsSemanaS-T
    "mensual": 719145147,               # KPIsMesS
    "mensual_comparado": 1657745862,    # KPIs_MesActual_vs_Anterior
}

}

COLUMNAS_UTILES = [
    "year", "nsemana", "codsalon", "codempleado", "facturacionsiva", "ticketmedio", "horasfichadas",
    "ratiogeneral", "ratiodesviaciontiempoteorico", "ratiotiempoindirecto", "ratioticketsinferior20"
]

def leer_kpis(year=None, nsemana=None, codsalon=None, tipo="semana"):
    hoja_id = HOJAS[tipo]
    url = f"{URL_GOOGLE_SHEET}&gid={hoja_id}"
    print(f"🌐 Consultando Google Sheet: {url}")
    df = pd.read_csv(url)

    df.columns = [col.lower().strip().replace(" ", "_") for col in df.columns]
    df = df.replace(["(en blanco)", "", "NA", "n/a"], pd.NA)

    for col in df.columns:
        if col in COLUMNAS_UTILES:
            df[col] = (
                df[col].astype(str)
                .str.replace(",", ".", regex=False)
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[[c for c in df.columns if c in COLUMNAS_UTILES]]

    if year is not None:
        df = df[df["year"] == year]
    if nsemana is not None:
        df = df[df["nsemana"] == nsemana]
    if codsalon is not None:
        df = df[df["codsalon"] == codsalon]

    print(f"📦 Columnas tras limpieza: {df.columns.tolist()}")
    print(f"📊 Total filas tras filtros: {len(df)}")
    print(df.head())

    return df.dropna(how="any")

def explicar_kpi(nombre_kpi):
    explicaciones = {
        "ratiogeneral": "Mide la facturación por hora trabajada.",
        "ticketmedio": "Promedio de facturación por ticket.",
        "horasfichadas": "Horas registradas por el personal.",
        "ratioticketsinferior20": "Porcentaje de tickets con importe menor a 20€.",
        "ratiotiempoindirecto": "Proporción del tiempo no facturable.",
        "ratiodesviaciontiempoteorico": "Desviación entre tiempo teórico y real."
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
    except Exception as e:
        return {"error": f"No se pudo calcular la variación entre semanas. ({e})"}

def analizar_trabajadores(df):
    if df.empty:
        return {"error": "El DataFrame está vacío tras filtrado."}

    if "codempleado" not in df.columns:
        return {"error": "No hay datos por trabajador (columna 'codempleado' no encontrada)."}

    resumen = df.groupby("codempleado").agg({
        "facturacionsiva": "sum",
        "ratiogeneral": "mean",
        "horasfichadas": "sum"
    }).reset_index()

    print("✅ Resumen por trabajador generado")
    return resumen.to_dict(orient="records")

def sugerencias_mejora(df):
    sugerencias = []
    if "ratiotiempoindirecto" in df.columns and df["ratiotiempoindirecto"].mean() > 0.3:
        sugerencias.append("Reducir el tiempo indirecto por debajo del 30%.")
    if "ratioticketsinferior20" in df.columns and df["ratioticketsinferior20"].mean() > 0.25:
        sugerencias.append("Mejorar la estrategia de upselling para tickets bajos.")
    return {"mejoras": sugerencias}

