# funciones/explicar_ratio_diario.py

import httpx
import pandas as pd
from funciones.utils import formatear_porcentaje

API_BASE = "https://bootdirectoras.onrender.com"
ENDPOINT_30DIAS = "/kpis/30dias"

def explicar_ratio_diario(codsalon: str, fecha: str) -> str:
    # 1️⃣ Llamada al endpoint interno
    resp = httpx.get(f"{API_BASE}{ENDPOINT_30DIAS}", params={"codsalon": codsalon}, timeout=10.0)
    resp.raise_for_status()
    payload = resp.json()

    # 2️⃣ Montar DataFrame
    df = pd.DataFrame(payload.get("datos", []))
    if df.empty:
        return f"Soy Mont Dirección. No hay datos registrados para el salón {codsalon} en la fecha {fecha}."

    # 3️⃣ Normalizar fechas y strings
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.date
    fecha_dt = pd.to_datetime(fecha).date()
    df["codsalon"] = df["codsalon"].astype(str)

    # 4️⃣ Filtrar por fecha y salón
    fila_df = df[(df["codsalon"] == codsalon) & (df["fecha"] == fecha_dt)]
    if fila_df.empty:
        return f"Soy Mont Dirección. No hay datos registrados para el salón {codsalon} el día {fecha}."

    row = fila_df.iloc[0]

    # 5️⃣ Extraer KPIs
    ratiogeneral     = row["ratiogeneral"] * 100
    facturacion      = row["facturacionsiva"]
    horas            = row["horasfichadas"]
    desviacion       = row["ratiodesviaciontiempoteorico"] * 100
    tiempo_indirecto = row["ratiotiempoindirecto"] * 100
    ratio_tickets    = row["ratioticketsinferior20"] * 100
    ticket_medio     = row["ticketsivamedio"]

    # 6️⃣ Clasificar y construir explicación
    saludo = f"¡Hola! Soy Mont Dirección. Vamos a ver el desempeño del salón {codsalon} el día {fecha}.\n\n"
    if ratiogeneral < 160:
        resumen = f"📊 Ratio General: {formatear_porcentaje(ratiogeneral)} (BAJO)."
    elif ratiogeneral < 200:
        resumen = f"📊 Ratio General: {formatear_porcentaje(ratiogeneral)} (ACEPTABLE)."
    else:
        resumen = f"📊 Ratio General: {formatear_porcentaje(ratiogeneral)} (EXCELENTE)."

    causas = []
    if desviacion < -5:
        causas.append("📅 Desviación negativa de la agenda (cancelaciones o retrasos).")
    elif desviacion > 5:
        causas.append("📅 Desviación positiva de la agenda (se cumplieron o superaron tiempos previstos).")
    if tiempo_indirecto > 20:
        causas.append("🧍‍♂️ Tiempo indirecto elevado (> 20%).")
    if ratio_tickets > 25:
        causas.append("🎟️ > 25% de tickets < 20 €, baja rentabilidad por visita.")
    if ticket_medio > 35:
        causas.append("💳 Ticket medio alto (> 35 €), muy positivo.")
    if facturacion < 300:
        causas.append("💰 Facturación baja (< 300 €).")
    if horas > 30:
        causas.append("⏱️ Muchas horas fichadas (> 30 h).")

    if not causas:
        causas_text = "✅ No se detectan desviaciones relevantes en los KPIs clave."
    else:
        causas_text = "Principales factores:\n- " + "\n- ".join(causas)

    return saludo + resumen + "\n\n" + causas_text

