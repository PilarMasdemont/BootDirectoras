
import re
from pathlib import Path
from unidecode import unidecode
from rapidfuzz import fuzz

def cargar_info_producto(nombre_producto: str) -> str:
    # Ruta al archivo productos.md
    ruta = Path(__file__).resolve().parent.parent / "datos_estaticos" / "productos.md"
    print("📁 Ruta absoluta del archivo productos.md:", ruta)

    if not ruta.exists():
        print("⚠️ Archivo productos.md no encontrado.")
        return "Lo siento, no se encuentra disponible la base de datos de productos en este momento."

    # Leer y dividir el contenido por secciones
    texto = ruta.read_text(encoding="utf-8")
    bloques = re.split(r"(?=^#|^IGORA|^WELLA|^SCHWARZKOPF|^L'ORÉAL|^L'OREAL)", texto, flags=re.MULTILINE)

    # Normalizar el nombre del producto
    nombre_normalizado = unidecode(nombre_producto.lower())

    # Buscar el bloque más parecido
    mejores_resultados = []
    for i, bloque in enumerate(bloques):
        titulo = bloque.strip().split("\n")[0]
        puntuacion = fuzz.token_sort_ratio(nombre_normalizado, unidecode(titulo.lower()))
        mejores_resultados.append((titulo, puntuacion, i))

    mejores_resultados.sort(key=lambda x: x[1], reverse=True)
    print("🔍 Resultados de matching:", mejores_resultados[:3])

    mejor_match = mejores_resultados[0]
    if mejor_match[1] < 60:
        print("❌ Ningún producto suficientemente parecido encontrado.")
        return f"No se encontró información específica para el producto '{nombre_producto}'."

    bloque_elegido = bloques[mejor_match[2]]
    print(f"✅ Producto detectado como match: '{mejor_match[0]}' con score {mejor_match[1]}")
    return bloque_elegido.strip()
