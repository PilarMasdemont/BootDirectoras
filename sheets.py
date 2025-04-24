import pandas as pd
import requests
from io import StringIO
import numpy as np
import re

def leer_kpis(year=None, nsemana=None, codsalon=None, tipo="semana"):
    sheet_id = "1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0"
    gid_map = {
        "semana": "2036398995",
        "trabajadores": "31094205",
        "mensual": "1333792005"
    }

    if tipo not in gid_map:
        raise ValueError(f"Tipo de hoja desconocido: '{tipo}'")

    gid = gid_map[tipo]
    SHEET_URL = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    print(f"\U0001f310 Consultando Google Sheet ({tipo}): {SHEET_URL}")

    response = requests.get(SHEET_URL)
    print(f"\U0001f4e5 Estado de la respuesta: {response.status_code}")

    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code}: {response.reason}")

    csv_text = response.text
    df = pd.read_csv(StringIO(csv_text), sep=",")
    df.columns = df.columns.str.strip().str.lower()
    print("\U0001f50e Columnas detectadas:", df.columns.tolist())

    columnas_filtro = [col for col in ['year', 'nsemana', 'codsalon'] if col in df.columns]
    for col in columnas_filtro:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Limpiar todos los valores con símbolos y convertir a float
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).apply(lambda x: re.sub(r'[%€]', '', x).strip())
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if year is not None and 'year' in df.columns:
        df = df[df['year'] == year]
    if nsemana is not None and 'nsemana' in df.columns:
        df = df[df['nsemana'] == nsemana]
    if codsalon is not None and 'codsalon' in df.columns:
        df = df[df['codsalon'] == codsalon]

    print(f"\U0001f4ca Filas tras aplicar filtros: {len(df)}")

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df = df.where(pd.notnull(df), None)

    return df


def analizar_trabajadores(df):
    coeficientes = {
        "ratiotiempoindirecto": -0.74,
        "ratiodesviaciontiempoteorico": -0.25,
        "ratioticketsinferior20": -0.19,
        "horasfichadas": -0.04
    }

    resultados = []

    for _, row in df.iterrows():
        impacto_total = 0
        positivos = []
        negativos = []
        mejoras = []

        for kpi, peso in coeficientes.items():
            valor = row[kpi] if pd.notnull(row[kpi]) else 0
            impacto_kpi = valor * peso
            impacto_total += impacto_kpi

            if peso < 0 and valor > 0.2:
                negativos.append(kpi)
                mejoras.append({"kpi": kpi, "impacto": round(impacto_kpi, 2)})
            elif peso < 0 and valor <= 0.2:
                positivos.append(kpi)

        resultado = {
            "codempleado": int(row["codempleado"]),
            "ratiogeneral": round(row["ratiogeneral"], 2) if pd.notnull(row["ratiogeneral"]) else None,
            "impacto_total": round(impacto_total, 2),
            "prioridad": None,
            "positivos": positivos,
            "negativos": negativos,
            "mejoras": mejoras
        }
        resultados.append(resultado)

    resultados.sort(key=lambda x: x["impacto_total"])
    for i, r in enumerate(resultados):
        r["prioridad"] = i + 1

    return resultados


def analizar_salon(df):
    coeficientes = {
        "ratiotiempoindirecto": -0.74,
        "ratiodesviaciontiempoteorico": -0.25,
        "ratioticketsinferior20": -0.19,
        "horasfichadas": -0.04
    }

    promedio = df.mean(numeric_only=True)
    impacto_total = 0
    positivos = []
    negativos = []
    mejoras = []

    for kpi, peso in coeficientes.items():
        valor = promedio.get(kpi, 0)
        impacto_kpi = valor * peso
        impacto_total += impacto_kpi

        if peso < 0 and valor > 0.2:
            negativos.append(kpi)
            mejoras.append({"kpi": kpi, "impacto": round(impacto_kpi, 2)})
        elif peso < 0 and valor <= 0.2:
            positivos.append(kpi)

    return {
        "ratiogeneral": round(promedio.get("ratiogeneral", 0), 2),
        "impacto_total": round(impacto_total, 2),
        "positivos": positivos,
        "negativos": negativos,
        "mejoras": mejoras
    }
