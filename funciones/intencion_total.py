# funciones/intencion_total.py
from funciones.intencion import clasificar_intencion as clasificar_general
from funciones.intention_process import clasificar_intencion as clasificar_proceso
from funciones.intention_producto import clasificar_intencion_producto as clasificar_producto
from funciones.extractores_proceso import extraer_nombre_proceso, extraer_duda_proceso
from funciones.extractores_producto import extraer_nombre_producto, extraer_duda_producto
from funciones.consultar_producto_con_chatgpt import consultar_producto_chatgpt as consultar_producto

def clasificar_intencion_completa(texto: str) -> dict:
    texto = texto.strip().lower()

    # Paso 1: Detectar si es sobre procesos
    resultado_proceso = clasificar_proceso(texto)
    if resultado_proceso.get("intencion") == "consultar_proceso":
        return {
            "intencion": "consultar_proceso",
            "comentario": resultado_proceso.get("comentario"),
            "proceso": extraer_nombre_proceso(texto),
            "atributo": extraer_duda_proceso(texto),
            "tiene_fecha": False
        }

    # Paso 2: Detectar si es sobre productos
    resultado_producto = clasificar_producto(texto)
    if resultado_producto.get("intencion") == "consultar_producto":
        return {
            "intencion": "consultar_producto",
            "comentario": resultado_producto.get("comentario"),
            "producto": extraer_nombre_producto(texto),
            "atributo": extraer_duda_producto(texto),
            "tiene_fecha": False
        }

    # Paso 3: Solo si contiene fecha, clasificar como general
    contiene_fecha = any(p in texto for p in [
        "hoy", "ayer", "semana", "mes", "lunes", "martes",
        "miércoles", "jueves", "viernes", "sábado", "domingo"
    ])

    if contiene_fecha:
        resultado_general = clasificar_general(texto)
        return {
            "intencion": resultado_general.get("intencion", "desconocida"),
            "comentario": resultado_general.get("comentario"),
            "tiene_fecha": True
        }

    # No se detectó intención clara
    return {
        "intencion": "desconocida",
        "comentario": "No se detecta intención clara",
        "tiene_fecha": False
    }








