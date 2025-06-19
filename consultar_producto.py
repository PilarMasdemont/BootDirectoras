from funciones.extractores_producto import extraer_nombre_producto, explicar_producto

def consultar_producto(texto_usuario: str) -> dict:
    nombre_producto = extraer_nombre_producto(texto_usuario)

    if not nombre_producto:
        return {
            "tipo": "respuesta_directa",
            "contenido": "Lo siento, no pude identificar el producto al que te refieres."
        }

    explicacion = explicar_producto(nombre_producto)

    return {
        "tipo": "respuesta_directa",
        "contenido": explicacion
    }
