from pathlib import Path

def cargar_info_producto():
    ruta = Path("datos_estaticos/productos.md")
    print("Ruta absoluta del archivo productos.md:", ruta.resolve())
    if not ruta.exists():
        raise FileNotFoundError("El archivo productos.md no se encuentra en la carpeta 'datos_estaticos'.")
    return ruta.read_text(encoding="utf-8")

