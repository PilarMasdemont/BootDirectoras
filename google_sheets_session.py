# google_sheets_session.py

import pandas as pd
from sheets_io import cargar_hoja_por_nombre, guardar_hoja
from datetime import datetime, date

SHEET_ID = "1YvWEySbojGoCrHqPyUb_VXNvcZOJNhfx8cEXPI4zHPc"
TABLA_SESIONES = "session_state"

# Columnas esperadas para session_state
NAMESPACE = [
    "ip_usuario", "fecha", "indice_empleado", "modo", "codsalon",
    "ultima_interaccion", "codempleado", "nsemana", "mes", "kpi", "fecha_anterior"
]

def cargar_sesion(ip: str, fecha: str) -> dict:
    """
    Carga la sesión de un usuario para una fecha dada.
    Devuelve un diccionario con el estado de la sesión o uno nuevo si no existe.
    """
    try:
        df = cargar_hoja_por_nombre(SHEET_ID, TABLA_SESIONES)
        df.columns = [str(col).lower().replace(" ", "_") for col in df.columns]
        print(f"📋 Columnas tras normalizar: {df.columns.tolist()}")

        if "ip_usuario" not in df.columns or "fecha" not in df.columns:
            raise KeyError("Columnas de sesión no presentes en la hoja.")

        df["ip_usuario"] = df["ip_usuario"].astype(str)
        df["fecha"] = df["fecha"].astype(str)

        row = df[(df["ip_usuario"] == ip) & (df["fecha"] == fecha)]
        if not row.empty:
            r = row.iloc[0].to_dict()
            print(f"📂 Sesión encontrada: {r}")
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
        print(f"❌ Error al cargar sesión: {e}")

    # Usar fecha actual si no se proporciona
    fecha_hoy = fecha if fecha else date.today().isoformat()
    print(f"📂 No se encontró sesión: creando nueva para ip={ip}, fecha={fecha_hoy}")
    return {"ip_usuario": ip, "fecha": fecha_hoy, "indice_empleado": 0}


def guardar_sesion(sesion: dict):
    """
    Guarda/actualiza la sesión del usuario en la hoja de Google Sheets.
    """
    try:
        df = cargar_hoja_por_nombre(SHEET_ID, TABLA_SESIONES)
        df.columns = [str(col).lower().replace(" ", "_") for col in df.columns]
        print(f"📋 Columnas tras normalizar: {df.columns.tolist()}")

        if not df.columns.tolist():
            df = pd.DataFrame(columns=NAMESPACE)
            print(f"🆕 Creando nueva estructura de sesión con columnas: {NAMESPACE}")

        df["ip_usuario"] = df["ip_usuario"].astype(str)
        df["fecha"] = df["fecha"].astype(str)

        ip = str(sesion.get("ip_usuario", ""))
        fecha = sesion.get("fecha") or date.today().isoformat()

        datos = {
            "ip_usuario": ip,
            "fecha": fecha,
            "indice_empleado": sesion.get("indice_empleado", 0),
            "modo": sesion.get("modo", ""),
            "codsalon": sesion.get("codsalon", ""),
            "ultima_interaccion": datetime.now().strftime("%H:%M"),
            "codempleado": sesion.get("codempleado", ""),
            "nsemana": sesion.get("nsemana", ""),
            "mes": sesion.get("mes", ""),
            "kpi": sesion.get("kpi", ""),
            "fecha_anterior": sesion.get("fecha_anterior", "")
        }

        print(f"📄 Datos de sesión a guardar: {datos}")
        mask = (df["ip_usuario"] == ip) & (df["fecha"] == fecha)

        if mask.any():
            print("✏️ Actualizando fila existente.")
            for key, val in datos.items():
                if key in df.columns:
                    try:
                        if pd.api.types.is_integer_dtype(df[key]):
                            df.loc[mask, key] = int(val)
                        else:
                            df.loc[mask, key] = val
                    except Exception as warn:
                        print(f"⚠️ Problema al asignar {key}: {warn}")
        else:
            print("➕ Agregando nueva fila.")
            df = pd.concat([df, pd.DataFrame([datos])], ignore_index=True)

        print(f"📂 Guardando hoja con {len(df)} filas.")
        guardar_hoja(SHEET_ID, TABLA_SESIONES, df)
        print("✅ Sesión guardada correctamente.")
    except Exception as e:
        print(f"❌ Error al guardar sesión: {e}")

