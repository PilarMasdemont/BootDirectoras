# Crear un archivo que consulte correctamente `productos.md` con ruta segura

codigo_seguro = """
import os

def cargar_info_producto():
    basedir = os.path.dirname(os.path.abspath(__file__))
    print("Ruta absoluta del archivo productos.md:", ruta.resolve())  # 👈 Añade esta línea aquí
    ruta_productos = os.path.join(basedir, "..", "datos_estaticos", "productos.md")

    try:
        with open(ruta_productos, "r", encoding="utf-8") as f:
            contenido = f.read()
        return contenido
    except FileNotFoundError:
        return "⚠ No se encontró el archivo de productos en la ruta esperada."
    except Exception as e:
        return f"❌ Error al leer el archivo de productos: {e}"
"""

# Guardar como archivo Python
path_seguro = "/mnt/data/cargar_productos_seguro.py"
with open(path_seguro, "w", encoding="utf-8") as f:
    f.write(codigo_seguro.strip())

path_seguro
