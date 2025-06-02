import os
from pathlib import Path

def cargar_info_producto(nombre_producto: str, campo_especifico: str = None) -> str:
    """
    Busca información sobre un producto en un archivo Markdown y retorna su contenido.

    Args:
        nombre_producto (str): El nombre del producto a buscar.
        campo_especifico (str, opcional): Si se proporciona, solo devuelve ese campo.

    Returns:
        str: Información del producto o mensaje de no encontrado.
    """
    from unidecode import unidecode

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

    for bloque in productos:
        bloque_limpio = unidecode(bloque.lower())
        if nombre_normalizado in bloque_limpio:
            if campo_especifico:
                campo = campo_especifico.lower()
                lineas = bloque.strip().splitlines()
                for linea in lineas:
                    if linea.lower().startswith(f"**{campo}**:"):
                        return linea.replace(f"**{campo_especifico}**:", "").strip()
                return f"⚠️ El campo '{campo_especifico}' no fue encontrado para el producto solicitado."
            return bloque.strip()

    return f"⚠️ El producto '{nombre_producto}' no se encuentra registrado en la base de datos."
