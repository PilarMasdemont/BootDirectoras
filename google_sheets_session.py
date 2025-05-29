# google_sheets_session.py

import pandas as pd
from sheets_io import cargar_hoja_por_nombre, guardar_hoja
from datetime import datetime

SHEET_ID = "1YvWEySbojGoCrHqPyUb_VXNvcZOJNhfx8cEXPI4zHPc"
TABLA_SESIONES = "session_state"
SHEET_PRODUCTOS_ID = "1GcTc0MJsLE-UKS1TylYkn8qF_wjurxV2pKfGbugtb5M"
GID_PRODUCTOS = "0"

def cargar_sesion(ip: str, fecha: str) -> dict:
    try:
        df = cargar_hoja_por_nombre(SHEET_ID, TABLA_SESIONES)
        # Normalizar nombres de columnas sin usar .str para evitar errores de tipo
        df.columns = [str(col).lower().replace(" ", "_") for col in df.columns]

        # Asegurar tipos string en columnas clave
        if "ip_usuario" in df.columns:
            df["ip_usuario"] = df["ip_usuario"].astype(str)
        if "fecha" in df.columns:
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
    # Si no existe, devolver contexto vacío
    return {"ip_usuario": ip, "fecha": fecha, "indice_empleado": 0}


def guardar_sesion(sesion: dict):
    try:
        print("📌 Iniciando guardado de sesión.")
        df = cargar_hoja_por_nombre(SHEET_ID, TABLA_SESIONES)
        print("📥 Hoja cargada correctamente.")

        # Normalizar nombres de columnas sin usar .str para evitar errores de tipo
        df.columns = [str(col).lower().replace(" ", "_") for col in df.columns]
        print("📋 Columnas normalizadas:", df.columns.tolist())

        # Evitar errores al castear
        if "ip_usuario" in df.columns:
            df["ip_usuario"] = df["ip_usuario"].astype(str)
        if "fecha" in df.columns:
            df["fecha"] = df["fecha"].astype(str)

        ip = str(sesion.get("ip_usuario", ""))
        fecha = str(sesion.get("fecha", ""))
        indice = sesion.get("indice_empleado", 0)
        modo = sesion.get("modo", "")
        codsalon = sesion.get("codsalon", "")
        codempleado = sesion.get("codempleado", "")
        nsemana = sesion.get("nsemana", "")
        mes = sesion.get("mes", "")
        kpi = sesion.get("kpi", "")
        fecha_anterior = sesion.get("fecha_anterior", "")
        ahora = datetime.now().strftime("%H:%M")

        print(f"📄 Datos sesión: ip={ip}, fecha={fecha}, indice={indice}")

        mask = (df["ip_usuario"] == ip) & (df["fecha"] == fecha)
        if mask.any():
            print("✏️ Actualizando fila existente.")
            df.loc[mask, [
                "indice_empleado", "modo", "codsalon", "ultima_interaccion",
                "codempleado", "nsemana", "mes", "kpi", "fecha_anterior"
            ]] = [
                indice, modo, codsalon, ahora,
                codempleado, nsemana, mes, kpi, fecha_anterior
            ]
        else:
            print("➕ Agregando nueva fila.")
            nueva_fila = pd.DataFrame([{  # Construir nueva fila
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

        print("💾 Guardando hoja final con shape:", df.shape)
        guardar_hoja(SHEET_ID, TABLA_SESIONES, df)
        print("✅ Sesión guardada correctamente.")
    except Exception as e:
        print(f"❌ Error al guardar sesión: {e}")
def buscar_producto_por_nombre_o_alias(nombre_producto: str) -> dict:
    try:
        hoja_productos = cargar_hoja_por_nombre(SHEET_PRODUCTOS_ID, GID_PRODUCTOS)
        hoja_productos.columns = [str(c).strip().lower().replace(" ", "_") for c in hoja_productos.columns]

        nombre_producto = nombre_producto.lower().strip()

        for _, fila in hoja_productos.iterrows():
            nombre = str(fila.get("nombre", "")).lower()
            aliases_raw = fila.get("aliases", "")
            aliases = [a.strip().lower() for a in str(aliases_raw).split(",") if a.strip()]

            if nombre_producto in nombre or any(nombre_producto in alias for alias in aliases):
                return fila.to_dict()
    except Exception as e:
        print(f"❌ Error al buscar producto: {e}")

    return {}

def cargar_aliases_productos():
    try:
        SHEET_ID = "1GcTc0MJsLE-UKS1TylYkn8qF_wjurxV2pKfGbugtb5M"
        GID_PRODUCTOS = "0"
        df = cargar_hoja_por_nombre(SHEET_ID, GID_PRODUCTOS)

        # Normalizar nombres de columnas
        df.columns = [col.lower().strip().replace(" ", "_") for col in df.columns]
        print("📋 Columnas normalizadas:", df.columns.tolist())

        # Limpiar valores no válidos
        df = df.replace(["(en blanco)", "", "NA", "n/a"], pd.NA)

        return df
    except Exception as e:
        print(f"❌ Error al cargar hoja de productos: {e}")
        return pd.DataFrame()  # Para que no falle el flujo


