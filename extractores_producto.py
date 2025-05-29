import pandas as pd
import re
from rapidfuzz import process, fuzz
from google_sheets_session import cargar_productos_catalogo


def normalizar(texto):
    """Limpia y convierte a minúsculas el texto."""
    if not isinstance(texto, str):
        return ""
    return re.sub(r"\s+", " ", texto.lower().strip())


def extraer_nombre_producto(texto_usuario: str) -> dict:
    """
    Extrae el nombre de producto más parecido desde el catálogo.

    Usa coincidencia difusa con rapidfuzz considerando nombre y aliases.
    """
    try:
        productos_df = cargar_productos_catalogo()
    except Exception as e:
        return {
            "nombre_producto": None,
            "comentario": f"❌ Error al cargar hoja de productos: {e}"
        }

    # Normalizar columnas
    productos_df.columns = [col.lower().strip().replace(" ", "_") for col in productos_df.columns]

    if "nombre" not in productos_df.columns or "aliases" not in productos_df.columns:
        return {
            "nombre_producto": None,
            "comentario": "❌ Faltan columnas necesarias ('nombre' o 'aliases') en la hoja de productos"
        }

    productos_df["nombre"] = productos_df["nombre"].fillna("").apply(normalizar)
    productos_df["aliases"] = productos_df["aliases"].fillna("").apply(normalizar)

    texto_usuario = normalizar(texto_usuario)

    # Generar lista de posibles alias y nombres
    candidatos = []
    for _, row in productos_df.iterrows():
        candidatos.append((row["nombre"], row["nombre"]))  # (texto, valor_retorno)
        for alias in row["aliases"].split(","):
            alias = alias.strip()
            if alias:
                candidatos.append((alias, row["nombre"]))

    # Buscar coincidencia
    mejor_match, score, nombre_canonico = None, 0, None
    if candidatos:
        mejor_match, score = process.extractOne(texto_usuario, [c[0] for c in candidatos], scorer=fuzz.token_sort_ratio)
        for alias, nombre in candidatos:
            if alias == mejor_match:
                nombre_canonico = nombre
                break

    if score >= 70:
        return {
            "nombre_producto": nombre_canonico,
            "comentario": f"✅ Producto encontrado por coincidencia: '{mejor_match}' (score: {score})"
        }
    else:
        return {
            "nombre_producto": None,
            "comentario": f"❌ Ningún producto coincide lo suficiente (score: {score})"
        }

