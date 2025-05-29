from rapidfuzz import fuzz
from google_sheets_session import cargar_aliases_productos
import pandas as pd
import re


def limpiar_texto(texto: str) -> str:
    if not isinstance(texto, str):
        return ""
    return re.sub(r"[^\w\s]", "", texto).lower().strip()


def extraer_nombre_producto(texto_usuario: str) -> dict:
    try:
        print(f"🔍 Buscando producto en texto: '{texto_usuario}'")

        texto_usuario = limpiar_texto(texto_usuario)
        productos_df = cargar_aliases_productos()

        if productos_df.empty:
            raise ValueError("El DataFrame de productos está vacío")

        productos_df.columns = [col.lower().strip().replace(" ", "_") for col in productos_df.columns]

        if "nombre" not in productos_df.columns or "aliases" not in productos_df.columns:
            raise KeyError("Faltan columnas requeridas: 'nombre' y/o 'aliases'")

        productos_df["nombre"] = productos_df["nombre"].fillna("").astype(str)
        productos_df["aliases"] = productos_df["aliases"].fillna("").astype(str)

        mejor_score = 0
        mejor_fila = None

        for _, fila in productos_df.iterrows():
            nombre = limpiar_texto(fila["nombre"])
            aliases = [limpiar_texto(alias) for alias in fila["aliases"].split(",")]
            candidatos = [nombre] + aliases

            for candidato in candidatos:
                score = fuzz.partial_ratio(texto_usuario, candidato)
                if score > mejor_score:
                    mejor_score = score
                    mejor_fila = fila

        if mejor_score >= 80 and mejor_fila is not None:
            print(f"✅ Producto detectado: {mejor_fila['nombre']} (score: {mejor_score})")
            return mejor_fila.to_dict()
        else:
            print("❌ No se encontró un producto con coincidencia suficiente.")
            return {"nombre_producto": "PRODUCTO_NO_ENCONTRADO", "comentario": "No se detectó producto válido."}

    except Exception as e:
        print(f"❌ Error durante la extracción del nombre de producto: {e}")
        return {"nombre_producto": "PRODUCTO_NO_ENCONTRADO", "comentario": "Respuesta no interpretable"}

