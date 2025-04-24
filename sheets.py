
import pandas as pd
import requests
from io import StringIO
import numpy as np
import re
import math

def safe_json(obj):
    if isinstance(obj, float):
        if math.isinf(obj) or math.isnan(obj):
            return None
        return obj
    elif isinstance(obj, list):
        return [safe_json(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: safe_json(v) for k, v in obj.items()}
    else:
        return obj

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
    print(f"🌐 Consultando Google Sheet ({tipo}): {SHEET_URL}")

    response = requests.get(SHEET_URL)
    print(f"📥 Estado de la respuesta: {response.status_code}")

    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code}: {response.reason}")

    csv_text = response.text
    df = pd.read_csv(StringIO(csv_text), sep=",")
    df.columns = df.columns.str.strip().str.lower()
    print("🔎 Columnas detectadas:", df.columns.tolist())

    columnas_filtro = [col for col in ['year', 'nsemana', 'codsalon'] if col in df.columns]
    for col in columnas_filtro:
        df[col] = pd.to_numeric(df[col], errors='coerce')

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

    print(f"📊 Filas tras aplicar filtros: {len(df)}")

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
            valor = pd.to_numeric(row.get(kpi), errors='coerce')
            valor = valor if pd.notnull(valor) else 0
            impacto_kpi = valor * peso
            impacto_total += impacto_kpi

            if peso < 0 and valor > 0.2:
                negativos.append(kpi)
                mejoras.append({"kpi": kpi, "impacto": round(impacto_kpi, 2)})
            elif peso < 0 and valor <= 0.2:
                positivos.append(kpi)

        resultado = {
            "codempleado": int(row.get("codempleado", -1)),
            "ratiogeneral": round(pd.to_numeric(row.get("ratiogeneral"), errors='coerce') or 0, 2),
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

    try:
        df = df.copy()
        for kpi in coeficientes:
            df[kpi] = pd.to_numeric(df[kpi], errors='coerce')

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

        return safe_json({
            "ratiogeneral": round(promedio.get("ratiogeneral", 0), 2),
            "impacto_total": round(impacto_total, 2),
            "positivos": positivos,
            "negativos": negativos,
            "mejoras": mejoras
        })
    except Exception as e:
        print(f"⚠️ Error en analizar_salon: {e}")
        raise



