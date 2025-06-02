import difflib
from pathlib import Path

def cargar_info_producto(nombre_producto: str) -> str:
    ruta = Path(__file__).parent / "datos_estaticos" / "productos.md"

    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta.resolve()}")

    contenido = ruta.read_text(encoding='utf-8')

    # Dividir por secciones de productos (asumiendo que empiezan con '###')
    secciones = contenido.split("### ")
    productos = {}
    
    for seccion in secciones:
        if not seccion.strip():
            continue
        lineas = seccion.splitlines()
        titulo = lineas[0].strip()
        cuerpo = "\n".join(lineas[1:]).strip()
        productos[titulo] = cuerpo

    # Buscar coincidencia aproximada con el nombre del producto
    coincidencia = difflib.get_close_matches(nombre_producto.strip().lower(), productos.keys(), n=1, cutoff=0.4)

    if coincidencia:
        titulo_match = coincidencia[0]
        resultado = f"### {titulo_match}\n{productos[titulo_match]}"
        print(f"[PRODUCTO] Coincidencia encontrada: {titulo_match}")
        return resultado
    else:
        print("[PRODUCTO] No se encontró ninguna coincidencia.")
        return "No he encontrado información sobre ese producto."

