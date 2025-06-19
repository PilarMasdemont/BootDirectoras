from funciones.extractores_producto import extraer_nombre_producto

def es_intencion_producto(texto_usuario: str) -> bool:
    """
    Determina si el usuario está preguntando por un producto.
    Devuelve True si se identifica un producto, False si no.
    """
    nombre_producto = extraer_nombre_producto(texto_usuario)
    return bool(nombre_producto)
