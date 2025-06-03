from pathlib import Path

codigo = """
from pathlib import Path
from rapidfuzz import process, fuzz

def cargar_info_producto(nombre_producto: str) -> str:
    ruta = Path(__file__).parent.parent / "datos_estaticos" / "productos.md"
    if not ruta.exists():
        return f"No se encontró el archivo de productos en: {ruta.resolve()}"

    contenido = ruta.read_text(encoding="utf-8")

    # Extraer productos
    bloques = contenido.split("### Producto:")
    productos = {}
    for bloque in bloques[1:]:
        lineas = bloque.strip().splitlines()
        if not lineas:
            continue
        nombre = lineas[0].strip()
        descripcion = "\\n".join(lineas[1:]).strip()
        productos[nombre.lower()] = f"### Producto: {nombre}\\n{descripcion}"

    nombres_productos = list(productos.keys())
    resultados = process.extract(nombre_producto.lower(), nombres_productos, scorer=fuzz.token_sort_ratio, limit=3)

    encontrados = [productos[nombre] for nombre, score, _ in resultados if score > 60]
    if not encontrados:
        return f"No se encontró información sobre ese producto. Intenta con otro nombre."

    contexto = "\\n\\n---\\n\\n".join(encontrados)
    prompt = (
        f"Usuario ha preguntado: '{nombre_producto}'\\n\\n"
        f"Consulta relacionada con uno o más productos.\\n"
        f"A continuación tienes información relevante:\\n\\n"
        f"{contexto}\\n\\n"
        f"Responde como Mont Dirección."
    )
    return prompt
"""

ruta_salida = Path("/mnt/data/cargar_productos_rapidfuzz.py")
ruta_salida.write_text(codigo.strip(), encoding="utf-8")
ruta_salida.name
