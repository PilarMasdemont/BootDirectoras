import pandas as pd
import numpy as np

URLS = {
    "semana": "https://docs.google.com/spreadsheets/d/1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0/export?format=csv&gid=2036398995",
    # Puedes añadir otros si lo necesitas
}

def leer_kpis(year=None, nsemana=None, codsalon=None, tipo="semana"):
    url = URLS[tipo]
    df = pd.read_csv(url)

    # Limpieza básica
    df = df.replace('(en blanco)', np.nan)
    df = df.dropna(subset=["year", "nsemana", "codsalon"])
    
    df["year"] = df["year"].astype(int)
    df["nsemana"] = df["nsemana"].astype(int)
    df["codsalon"] = df["codsalon"].astype(int)

    if year is not None:
        df = df[df["year"] == year]
    if nsemana is not None:
        df = df[df["nsemana"] == nsemana]
    if codsalon is not None:
        df = df[df["codsalon"] == codsalon]

    return df

def analizar_salon(df):
    resultado = {
        "ratiogeneral": None,
        "impacto_total": None,
        "positivos": [],
        "negativos": [],
        "mejoras": []
    }

    if df.empty:
        return resultado

    try:
        ratiogeneral = df["ratiogeneral"].mean()
        resultado["ratiogeneral"] = float(np.round(ratiogeneral, 4))

        # Impacto: Ejemplo usando facturación sin IVA * ratio general
        impacto = df["facturacionsiva"].astype(float) * df["ratiogeneral"].astype(float)
        resultado["impacto_total"] = float(np.round(impacto.sum(), 2))

        # Puedes definir umbrales personalizados
        for _, row in df.iterrows():
            if row["ratiogeneral"] > 2:
                resultado["positivos"].append(f"Alto rendimiento en semana {int(row['nsemana'])}")
            elif row["ratiogeneral"] < 1:
                resultado["negativos"].append(f"Bajo rendimiento en semana {int(row['nsemana'])}")

    except Exception as e:
        resultado["error"] = str(e)

    return resultado
