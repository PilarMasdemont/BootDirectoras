import pandas as pd

def leer_kpis(year=None, nsemana=None, codsalon=None, tipo="semana"):
    url_map = {
        "semana": "https://docs.google.com/spreadsheets/d/1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0/export?format=csv&gid=2036398995",
        # añade aquí más si tienes otros tipos
    }

    url = url_map.get(tipo)
    if not url:
        raise ValueError(f"Tipo de hoja desconocido: {tipo}")

    df = pd.read_csv(url, dtype=str)  # leer como texto por seguridad

    # Eliminar filas sin valores clave
    df = df.dropna(subset=["year", "nsemana", "codsalon"])

    # Convertir identificadores a enteros
    df["year"] = df["year"].astype(int)
    df["nsemana"] = df["nsemana"].astype(int)
    df["codsalon"] = df["codsalon"].astype(int)

    # Convertir columnas numéricas
    numeric_cols = ["facturacionsiva", "ticketmedio", "horasfichadas", "ratiogeneral",
                    "ratiodesviaciontiempoteorico", "ratiotiempoindirecto", "ratioticketsinferior20"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Aplicar filtros
    if year is not None:
        df = df[df["year"] == year]
    if nsemana is not None:
        df = df[df["nsemana"] == nsemana]
    if codsalon is not None:
        df = df[df["codsalon"] == codsalon]

    print(f"📊 Filas tras filtros: {len(df)}")
    return df
