import os
from pathlib import Path
from unidecode import unidecode
from rapidfuzz import process, fuzz

def cargar_info_producto(nombre_producto: str, campo_especifico: str = None) -> str:
    """
    Busca información sobre un producto en un archivo Markdown y retorna su contenido.

    Args:
        nombre_producto (str): El nombre del producto a buscar.
        campo_especifico (str, opcional): Si se proporciona, solo devuelve ese campo.

    Returns:
        str: Información del producto o mensaje de no encontrado.
    """
    # Normalización del nombre
    nombre_normalizado = unidecode(nombre_producto.strip().lower())

    # Ruta al archivo markdown
    ruta = Path(__file__).resolve().parent.parent / "datos_estaticos" / "productos.md"
    print("Ruta absoluta del archivo productos.md:", ruta.resolve())

    if not ruta.exists():
        return "⚠️ No se encontró el archivo de productos."

    with open(ruta, "r", encoding="utf-8") as f:
        contenido = f.read()

    # Separar productos
    productos = contenido.split("\n---")

    # Extraer encabezados para usar en matching difuso
    encabezados = [unidecode(bloque.split('\n')[0].strip().lower()) for bloque in productos]

    # Buscar mejor coincidencia con rapidfuzz
    mejor_match = process.extractOne(nombre_normalizado, encabezados, scorer=fuzz.token_set_ratio)

    if not mejor_match or mejor_match[1] < 60:
        return f"⚠️ El producto '{nombre_producto}' no se encuentra registrado en la base de datos."

    idx = encabezados.index(mejor_match[0])
    bloque = productos[idx]

    if campo_especifico:
        campo = campo_especifico.lower()
        lineas = bloque.strip().splitlines()
        for linea in lineas:
            if linea.lower().startswith(f"**{campo}**:"):
                return linea.replace(f"**{campo_especifico}**:", "").strip()
        return f"⚠️ El campo '{campo_especifico}' no fue encontrado para el producto solicitado."

    return bloque.strip()
