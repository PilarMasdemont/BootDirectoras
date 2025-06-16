from funciones.intencion import clasificar_intencion as clasificar_general
from funciones.intention_process import clasificar_intencion as clasificar_proceso
from funciones.extractores_proceso import extraer_nombre_proceso, extraer_duda_proceso
import json
import os

# Cargar lista de productos desde el diccionario JSON
PRODUCTOS_PATH = "datos/productos_diccionario.json"
with open(PRODUCTOS_PATH, "r", encoding="utf-8") as f:
    PRODUCTOS_NOMBRES = list(json.load(f).keys())

def clasificar_intencion_completa(texto: str) -> dict:
    texto = texto.strip().lower()

    palabras_servicio = [
        "mechas", "queratina", "alisado", "coloración", "tratamiento", "brillo",
        "masdemont", "hidratar", "reparar", "cabello", "pelo", "tinte", "vegana"
    ]

    palabras_proceso = [
        "caja", "inventario", "cerrar", "cuadrar", "proceso", "tarea", "pedido", "stock"
    ]

    # 💡 Detectar si se está preguntando por un producto del JSON
    for nombre in PRODUCTOS_NOMBRES:
        if nombre.lower() in texto:
            return {
                "intencion": "consultar_producto",
                "producto": nombre,
                "atributo": extraer_duda_proceso(texto),  # Reutilizamos el extractor de atributo
                "comentario": f"Detectado producto '{nombre}' desde JSON",
                "tiene_fecha": False
            }

    if any(p in texto for p in palabras_proceso):
        return {
            "intencion": "consultar_proceso",
            "comentario": "Detectado como proceso interno",
            "proceso": extraer_nombre_proceso(texto),
            "atributo": extraer_duda_proceso(texto),
            "tiene_fecha": False
        }

    if any(p in texto for p in palabras_servicio):
        return {
            "intencion": "explicar_producto",
            "comentario": "Detectado como técnica o servicio de peluquería",
            "tiene_fecha": False
        }

    resultado_proceso = clasificar_proceso(texto)
    if resultado_proceso.get("intencion") == "consultar_proceso":
        return {
            "intencion": "consultar_proceso",
            "comentario": resultado_proceso.get("comentario"),
            "proceso": extraer_nombre_proceso(texto),
            "atributo": extraer_duda_proceso(texto),
            "tiene_fecha": False
        }

    resultado_general = clasificar_general(texto)
    return {
        "intencion": resultado_general.get("intencion", "desconocida"),
        "comentario": resultado_general.get("comentario"),
        "tiene_fecha": any(p in texto for p in [
            "hoy", "ayer", "semana", "mes", "lunes", "martes", "miércoles",
            "jueves", "viernes", "sábado", "domingo"
        ])
    }



