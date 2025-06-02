from pathlib import Path
import re
import difflib

def cargar_info_producto(nombre_producto, ruta_archivo='datos_estaticos/productos.md', umbral_similitud=0.5):
    ruta = Path(ruta_archivo)
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta.resolve()}")

    with ruta.open("r", encoding="utf-8") as f:
        contenido = f.read()

    # Separar el contenido por productos usando los títulos '## '
    productos = re.split(r"^##\s+", contenido, flags=re.MULTILINE)
    nombres_productos = []
    secciones_productos = []

    for producto in productos:
        lineas = producto.strip().split("\n")
        if lineas:
            nombre = lineas[0].strip()
            nombres_productos.append(nombre)
            secciones_productos.append(producto.strip())

    # Buscar la mejor coincidencia
    coincidencias = difflib.get_close_matches(nombre_producto, nombres_productos, n=1, cutoff=umbral_similitud)

    if coincidencias:
        indice = nombres_productos.index(coincidencias[0])
        return secciones_productos[indice]
    else:
        return None

# Mostrar función como archivo para el usuario
from ace_tools import save_file

ruta_archivo = "/mnt/data/cargar_productos_optimo.py"
with open(ruta_archivo, "w", encoding="utf-8") as f:
    f.write(inspect.getsource(cargar_info_producto))

save_file(ruta_archivo)
