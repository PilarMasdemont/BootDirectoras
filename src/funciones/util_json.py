import json
import os

def get_nested_value(data, ruta):
    """Extrae un valor desde un JSON usando una lista de claves (ruta)."""
    for clave in ruta:
        if isinstance(data, dict):
            data = data.get(clave, {})
        else:
            return None
    return data

def extraer_fragmentos_desde_rutas(rutas, carpeta_jsons="archivos_estaticos"):
    """Dado una lista de rutas, abre los archivos y extrae solo los fragmentos necesarios."""
    info_extraida = {}

    for item in rutas:
        nombre_archivo = item["documento"]
        ruta = item["ruta"]
        path_completo = os.path.join(carpeta_jsons, nombre_archivo)

        try:
            with open(path_completo, encoding="utf-8") as f:
                data = json.load(f)
            valor = get_nested_value(data, ruta)
            clave_id = f"{nombre_archivo}::{'/'.join(ruta)}"
            info_extraida[clave_id] = valor
        except Exception as e:
            print(f"❌ Error al procesar {nombre_archivo}: {e}")

    return info_extraida
