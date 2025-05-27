# google_sheets_session.py

import pandas as pd
from sheets import cargar_hoja, guardar_hoja  # Asumimos que ya tienes estas funciones
from datetime import datetime

SHEET_ID = "tu_id_de_sheets"
TABLA_SESIONES = "session_state"  # Nombre de la pestaña de sesiones


def cargar_sesion(ip: str, fecha: str) -> dict:
    try:
        df = cargar_hoja(SHEET_ID, TABLA_SESIONES)
        df.columns = df.columns.str.lower().str.replace(" ", "_")

        row = df[(df["ip_usuario"] == ip) & (df["fecha"] == fecha)]

        if not row.empty:
            r = row.iloc[0].to_dict()
            return {
                "ip_usuario": ip,
                "fecha": fecha,
                "codsalon": r.get("codsalon"),
                "modo": r.get("modo"),
                "indice_empleado": int(r.get("indice_empleado", 0)),
                "ultima_interaccion": r.get("ultima_interaccion")
            }
    except Exception as e:
        print(f"Error al cargar sesión: {e}")

    return {"ip_usuario": ip, "fecha": fecha, "indice_empleado": 0}  # contexto vacío


def guardar_sesion(sesion: dict):
    try:
        df = cargar_hoja(SHEET_ID, TABLA_SESIONES)
        df.columns = df.columns.str.lower().str.replace(" ", "_")

        ip = sesion["ip_usuario"]
        fecha = sesion["fecha"]
        indice = sesion.get("indice_empleado", 0)
        modo = sesion.get("modo", "")
        codsalon = sesion.get("codsalon", "")
        ahora = datetime.now().strftime("%H:%M")

        mask = (df["ip_usuario"] == ip) & (df["fecha"] == fecha)

        if mask.any():
            df.loc[mask, ["indice_empleado", "modo", "codsalon", "ultima_interaccion"]] = [
                indice, modo, codsalon, ahora
            ]
        else:
            nueva_fila = pd.DataFrame([{
                "ip_usuario": ip,
                "fecha": fecha,
                "indice_empleado": indice,
                "modo": modo,
                "codsalon": codsalon,
                "ultima_interaccion": ahora
            }])
            df = pd.concat([df, nueva_fila], ignore_index=True)

        guardar_hoja(SHEET_ID, TABLA_SESIONES, df)

    except Exception as e:
        print(f"Error al guardar sesión: {e}")
