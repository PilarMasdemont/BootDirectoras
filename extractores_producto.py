import re
import pandas as pd
from google_sheets_session import cargar_aliases_productos


def extraer_nombre_producto(texto: str) -> dict:
    """
    Extrae el nombre del producto mencionado en el texto, buscando coincidencias
    exactas o parciales con los nombres y alias de productos del catálogo.
    """
    try:
        texto = texto.lower().strip()
        print(f"🔍 Buscando producto en texto: '{texto}'")

        productos_df = cargar_aliases_productos()
        if productos_df.empty:
            print("❌ Error: El DataFrame de productos está vacío")
            return {
                "nombre_producto": "PRODUCTO_NO_ENCONTRADO",
                "comentario": "El DataFrame de productos está vacío"
            }

        if "nombre" not in productos_df.columns or "aliases" not in productos_df.columns:
            print("❌ Error: Faltan columnas requeridas en la hoja de productos")
            return {
                "nombre_producto": "PRODUCTO_NO_ENCONTRADO",
                "comentario": "Faltan columnas requeridas (nombre, aliases)"
            }

        productos_df["nombre"] = productos_df["nombre"].fillna("").astype(str)
        productos_df["aliases"] = productos_df["aliases"].fillna("").astype(str)

        for _, fila in productos_df.iterrows():
            nombre = fila["nombre"].lower()
            if nombre in texto:
                print(f"✅ Coincidencia exacta con nombre: {nombre}")
                return fila.to_dict()

            aliases = [alias.strip().lower() for alias in fila["aliases"].split(",") if alias.strip()]
            for alias in aliases:
                if alias in texto:
                    print(f"✅ Coincidencia con alias: {alias} para producto {nombre}")
                    return fila.to_dict()

        print("⚠️ No se encontró coincidencia para ningún producto")
        return {
            "nombre_producto": "PRODUCTO_NO_ENCONTRADO",
            "comentario": "No se encontró coincidencia con ningún producto del catálogo"
        }

    except Exception as e:
        print(f"❌ Error durante la extracción del nombre de producto: {e}")
        return {
            "nombre_producto": "PRODUCTO_NO_ENCONTRADO",
            "comentario": f"Excepción en la extracción: {e}"
        }
