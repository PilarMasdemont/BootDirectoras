import json
import re
import logging

from funciones.intencion import clasificar_intencion as clasificar_general
from funciones.intention_process import clasificar_intencion as clasificar_proceso
from funciones.intention_producto import es_intencion_producto
from funciones.extractores_proceso import extraer_nombre_proceso, extraer_duda_proceso
from funciones.extractores_producto import extraer_nombre_producto

def normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = re.sub(r"[^\w\sáéíóúüñ]", "", texto)  # eliminar puntuación
    texto = re.sub(r"\b\d+\s?(ml|g|gr|kg|l|litros)?\b", "", texto)  # elimina unidades
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

def clasificar_intencion_completa(texto: str) -> dict:
    texto_limpio = normalizar(texto)

    palabras_servicio = [
        "mechas", "queratina", "alisado", "coloración", "tratamiento", "brillo",
        "masdemont", "hidratar", "reparar", "cabello", "pelo", "tinte", "vegana"
    ]

    palabras_proceso = [
        "caja", "inventario", "cerrar", "cuadrar", "proceso", "tarea", "pedido", "stock"
    ]

    # 🧴 CONSULTAR PRODUCTO
    if es_intencion_producto(texto):
        nombre = extraer_nombre_producto(texto)
        return {
            "intencion": "consultar_producto",
            "producto": nombre,
            "comentario": f"Detectado producto '{nombre}' usando intención de producto",
            "tiene_fecha": False
        }

    # 🔁 CONSULTAR PROCESO
    if any(p in texto_limpio for p in palabras_proceso):
        return {
            "intencion": "consultar_proceso",
            "comentario": "Detectado como proceso interno",
            "proceso": extraer_nombre_proceso(texto),
            "atributo": extraer_duda_proceso(texto),
            "tiene_fecha": False
        }

    # ✂️ SERVICIO ESTÉTICO
    if any(p in texto_limpio for p in palabras_servicio):
        return {
            "intencion": "explicar_producto",
            "comentario": "Detectado como técnica o servicio de peluquería",
            "tiene_fecha": False
        }

    # 🔄 Fallback: clasificador específico de procesos
    resultado_proceso = clasificar_proceso(texto)
    if resultado_proceso.get("intencion") == "consultar_proceso":
        return {
            "intencion": "consultar_proceso",
            "comentario": resultado_proceso.get("comentario"),
            "proceso": extraer_nombre_proceso(texto),
            "atributo": extraer_duda_proceso(texto),
            "tiene_fecha": False
        }

    # 🌍 Fallback general
    resultado_general = clasificar_general(texto)
    return {
        "intencion": resultado_general.get("intencion", "desconocida"),
        "comentario": resultado_general.get("comentario"),
        "tiene_fecha": any(p in texto_limpio for p in [
            "hoy", "ayer", "semana", "mes", "lunes", "martes", "miércoles",
            "jueves", "viernes", "sábado", "domingo"
        ])
    }








