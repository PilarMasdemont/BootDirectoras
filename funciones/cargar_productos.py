import re
import json
import logging
from pathlib import Path
from rapidfuzz import fuzz, process

logger = logging.getLogger(__name__)

# Ruta al nuevo diccionario JSON
RUTA_JSON = Path("datos_estaticos/productos_diccionario.json")

# Umbral de similitud mínimo para considerar una coincidencia válida
UMBRAL_SIMILITUD = 50.0

def cargar_info_producto(nombre_producto: str) -> str:
    """
    Busca el producto más parecido usando el diccionario y devuelve su descripción si lo encuentra.
    """
    logger.info(f"📥 Producto solicitado: {nombre_producto}")

    if not RUTA_JSON.exists():
        logger.error(f"❌ Archivo de diccionario no encontrado: {RUTA_JSON}")
        return "No se pudo acceder a la base de datos de productos."

    try:
        productos = json.loads(RUTA_JSON.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"❌ Error al leer el diccionario JSON: {e}")
        return "No se pudo procesar el archivo de productos."

    nombres = list(productos.keys())
    resultados = process.extract(nombre_producto, nombres, scorer=fuzz.partial_ratio, limit=3)
    logger.info(f"🔍 Resultados de matching: {resultados}")

    for nombre_encontrado, similitud, _ in resultados:
        if similitud >= UMBRAL_SIMILITUD:
            descripcion = productos[nombre_encontrado]
            logger.info(f"✅ Producto encontrado: {nombre_encontrado} con similitud {similitud:.2f}")
            return descripcion

    logger.warning("❌ Ningún producto suficientemente parecido encontrado.")
    return f"Lo siento, no tengo información sobre el producto '{nombre_producto}'."

