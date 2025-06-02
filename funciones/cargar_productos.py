from pathlib import Path
import logging
import difflib

def cargar_info_producto(nombre_producto: str):
    ruta = Path("datos_estaticos/productos.md")
    logging.info(f"📄 Ruta absoluta del archivo productos.md: {ruta.resolve()}")

    if not ruta.exists():
        logging.error("❌ El archivo productos.md no se encuentra.")
        raise FileNotFoundError("El archivo productos.md no se encuentra.")

    contenido = ruta.read_text(encoding="utf-8").strip()
    if not contenido:
        logging.warning("⚠️ El archivo productos.md está vacío.")
        raise ValueError("El archivo productos.md está vacío.")

    # Dividir por secciones (cada producto empieza con '## ')
    secciones = contenido.split("## ")
    productos = {s.splitlines()[0].strip(): s for s in secciones if s.strip()}

    # Buscar coincidencia aproximada
    nombres = list(productos.keys())
    mejor_coincidencia = difflib.get_close_matches(nombre_producto, nombres, n=1, cutoff=0.4)

    if mejor_coincidencia:
        producto = mejor_coincidencia[0]
        logging.info(f"✅ Producto encontrado: {producto}")
        return f"## {productos[producto]}"
    else:
        logging.warning(f"❌ No se encontró una coincidencia para: {nombre_producto}")
        return None
