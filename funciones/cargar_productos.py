from pathlib import Path

# Código completo del nuevo archivo con la mejora solicitada
nuevo_codigo = """
import json
from rapidfuzz import process, fuzz
import logging
from pathlib import Path

# Configuración del logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Ruta al diccionario de productos
RUTA_JSON = Path("datos_estaticos/productos_diccionario.json")

# Umbral de similitud
UMBRAL_SIMILITUD = 60

def normalizar(texto: str) -> str:
    return texto.strip().lower().replace("-", " ").replace("_", " ")

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
        limit=10
    )

    logger.info("🔍 Resultados de matching:")
    for (match, score, index) in resultados:
        logger.info(f"   - {nombres_originales[index]} → {score:.2f}")

    if not resultados:
        logger.warning("❌ Ningún producto suficientemente parecido encontrado.")
        return f"Lo siento, no tengo información sobre el producto '{nombre_producto}'."

    max_score = max(score for _, score, _ in resultados)
    mejores = [(nombres_originales[i], score) for _, score, i in resultados if score == max_score and score >= UMBRAL_SIMILITUD]

    if not mejores:
        logger.warning("❌ Ningún producto suficientemente parecido encontrado.")
        return f"Lo siento, no tengo información sobre el producto '{nombre_producto}'."

    if len(mejores) == 1:
        nombre_real = mejores[0][0]
        logger.info(f"✅ Producto encontrado: {nombre_real} con similitud {mejores[0][1]:.2f}")
        return productos[nombre_real]

    logger.info(f"🔀 Múltiples coincidencias con score {max_score:.2f}, pidiendo confirmación al usuario")
    opciones = "\\n".join(f"- {nombre}" for nombre, _ in mejores)
    return (
        f"He encontrado varios productos muy similares:\\n\\n{opciones}\\n\\n"
        "Por favor, copia y pega el nombre exacto del producto que deseas consultar."
    )
"""

# Guardar el archivo
ruta_archivo = "/mnt/data/cargar_productos_mejorado.py"
Path(ruta_archivo).write_text(nuevo_codigo)

ruta_archivo

