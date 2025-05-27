# google_sheets_session.py

import pandas as pd
from sheets_io import cargar_hoja_por_nombre, guardar_hoja
from datetime import datetime

SHEET_ID = "1YvWEySbojGoCrHqPyUb_VXNvcZOJNhfx8cEXPI4zHPc"
TABLA_SESIONES = "session_state"

def cargar_sesion(ip: str, fecha: str) -> dict:
    try:
        df = cargar_hoja_por_nombre(SHEET_ID, TABLA_SESIONES)
        df.columns = df.columns.astype(str).str.lower().str.replace(" ", "_")

        df["ip_usuario"] = df["ip_usuario"].astype(str)
        df["fecha"] = df["fecha"].astype(str)

        row = df[(df["ip_usuario"] == ip) & (df["fecha"] == fecha)]

        if not row.empty:
            r = row.iloc[0].to_dict()
            return {
                "ip_usuario": ip,
                "fecha": fecha,
                "codsalon": r.get("codsalon"),
                "modo": r.get("modo"),
                "indice_empleado": int(r.get("indice_empleado", 0)),
                "ultima_interaccion": r.get("ultima_interaccion"),
                "codempleado": r.get("codempleado"),
                "nsemana": r.get("nsemana"),
                "mes": r.get("mes"),
                "kpi": r.get("kpi"),
                "fecha_anterior": r.get("fecha_anterior")
            }
    except Exception as e:
        print(f"Error al cargar sesión: {e}")

    return {"ip_usuario": ip, "fecha": fecha, "indice_empleado": 0}  # contexto vacío

def guardar_sesion(sesion: dict):
    try:
        df = cargar_hoja_por_nombre(SHEET_ID, TABLA_SESIONES)
        df.columns = df.columns.astype(str).str.lower().str.replace(" ", "_")

        df["ip_usuario"] = df["ip_usuario"].astype(str)
        df["fecha"] = df["fecha"].astype(str)

        ip = sesion["ip_usuario"]
        fecha = sesion["fecha"]
        indice = sesion.get("indice_empleado", 0)
        modo = sesion.get("modo", "")
        codsalon = sesion.get("codsalon", "")
        codempleado = sesion.get("codempleado", "")
        nsemana = sesion.get("nsemana", "")
        mes = sesion.get("mes", "")
        kpi = sesion.get("kpi", "")
        fecha_anterior = sesion.get("fecha_anterior", "")
        ahora = datetime.now().strftime("%H:%M")

        mask = (df["ip_usuario"] == ip) & (df["fecha"] == fecha)

        if mask.any():
            df.loc[mask, [
                "indice_empleado", "modo", "codsalon", "ultima_interaccion",
                "codempleado", "nsemana", "mes", "kpi", "fecha_anterior"
            ]] = [
                indice, modo, codsalon, ahora,
                codempleado, nsemana, mes, kpi, fecha_anterior
            ]
        else:
            nueva_fila = pd.DataFrame([{
                "ip_usuario": ip,
                "fecha": fecha,
                "indice_empleado": indice,
                "modo": modo,
                "codsalon": codsalon,
                "ultima_interaccion": ahora,
                "codempleado": codempleado,
                "nsemana": nsemana,
                "mes": mes,
                "kpi": kpi,
                "fecha_anterior": fecha_anterior
            }])

            print("🔄 Nueva fila generada:", nueva_fila.to_dict(orient="records"))

            df = pd.concat([df, nueva_fila], ignore_index=True)

        guardar_hoja(SHEET_ID, TABLA_SESIONES, df)

    except Exception as e:
        print(f"Error al guardar sesión: {e}")


