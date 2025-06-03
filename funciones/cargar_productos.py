import re
import json
import logging
from pathlib import Path
from rapidfuzz import fuzz, process

logger = logging.getLogger(__name__)

# Ruta al nuevo diccionario JSON
RUTA_JSON = Path("datos_estaticos/productos_diccionario.json")

# Umbral de similitud mínimo
UMBRAL_SIMILITUD = 50.0

def normalizar(texto: str) -> str:
    return re.sub(r'\s+', ' ', texto.strip().lower())


def cargar_info_producto(nombre_producto: str) -> str:
    logger.info(f"📥 Producto solicitado: {nombre_producto}")

    if not RUTA_JSON.exists():
        logger.error(f"❌ Archivo de diccionario no encontrado: {RUTA_JSON}")
        return "No se pudo acceder a la base de datos de productos."

    try:
        productos = json.loads(RUTA_JSON.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"❌ Error al leer el diccionario JSON: {e}")
        return "No se pudo procesar el archivo de productos."

    nombres_originales = list(productos.keys())
    nombres_normalizados = [normalizar(n) for n in nombres_originales]
    nombre_producto_normalizado = normalizar(nombre_producto)

    resultados = process.extract(
        nombre_producto_normalizado,
        nombres_normalizados,
        scorer=fuzz.partial_ratio,
        limit=5
    )

    logger.info("🔍 Resultados de matching:")
    for (match, score, index) in resultados:
        logger.info(f"   - {nombres_originales[index]} → {score:.2f}")

    candidatos = [(nombres_originales[idx], score) for match, score, idx in resultados if score >= UMBRAL_SIMILITUD]

    if not candidatos:
        logger.warning("❌ Ningún producto suficientemente parecido encontrado.")
        return f"Lo siento, no tengo información sobre el producto '{nombre_producto}'."

    if len(candidatos) == 1 or candidatos[0][1] > candidatos[1][1]:
        nombre_real = candidatos[0][0]
        logger.info(f"✅ Producto encontrado: {nombre_real} con similitud {candidatos[0][1]:.2f}")
        return productos[nombre_real]

    logger.info("🤔 Múltiples coincidencias posibles encontradas.")
    opciones = "\n".join([f"- {nombre}" for nombre, _ in candidatos])
    return (
        "He encontrado varios productos que coinciden con tu búsqueda:\n"
        f"{opciones}\n"
        "Por favor, copia y pega el nombre exacto del producto del que quieres información."
    )
    logger.info(f"📥 Producto solicitado: {nombre_producto}")

    if not RUTA_JSON.exists():
        logger.error(f"❌ Archivo de diccionario no encontrado: {RUTA_JSON}")
        return "No se pudo acceder a la base de datos de productos."

    try:
        productos = json.loads(RUTA_JSON.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"❌ Error al leer el diccionario JSON: {e}")
        return "No se pudo procesar el archivo de productos."

    nombres_originales = list(productos.keys())
    nombres_normalizados = [normalizar(n) for n in nombres_originales]
    nombre_producto_normalizado = normalizar(nombre_producto)

    resultados = process.extract(
        nombre_producto_normalizado,
        nombres_normalizados,
        scorer=fuzz.partial_ratio,
        limit=5
    )

    logger.info("🔍 Resultados de matching:")
    for (match, score, index) in resultados:
        logger.info(f"   - {nombres_originales[index]} → {score:.2f}")

    mejor_match = max(resultados, key=lambda x: x[1], default=None)

    if mejor_match and mejor_match[1] >= UMBRAL_SIMILITUD:
        nombre_real = nombres_originales[mejor_match[2]]
        logger.info(f"✅ Producto encontrado: {nombre_real} con similitud {mejor_match[1]:.2f}")
        return productos[nombre_real]

    logger.warning("❌ Ningún producto suficientemente parecido encontrado.")
    return f"Lo siento, no tengo información sobre el producto '{nombre_producto}'."
