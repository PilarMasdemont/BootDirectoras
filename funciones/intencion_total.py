from funciones.intencion import clasificar_intencion as clasificar_general
from funciones.intention_process import clasificar_intencion as clasificar_proceso
from funciones.extractores_proceso import extraer_nombre_proceso, extraer_duda_proceso
import json
import os
import re
import logging

def normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = re.sub(r"[^\w\sáéíóúüñ]", "", texto)  # eliminar puntuación excepto tildes y letras válidas
    texto = re.sub(r"\b\d+\s?(ml|g|gr|kg|l|litros)?\b", "", texto)  # elimina unidades
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

# 📦 Cargar nombres de productos del JSON
PRODUCTOS_PATH = "Archivos_estaticos/productos_diccionario.json"
with open(PRODUCTOS_PATH, "r", encoding="utf-8") as f:
    PRODUCTOS_JSON = json.load(f)
    PRODUCTOS_NOMBRES = list(PRODUCTOS_JSON.keys())
    PRODUCTOS_NOMBRES_NORMALIZADOS = {
        normalizar(nombre): nombre for nombre in PRODUCTOS_NOMBRES
    }
    logging.info("🔍 Lista de productos normalizados:")
    for n in PRODUCTOS_NOMBRES_NORMALIZADOS:
        logging.info(f"- {n}")


def clasificar_intencion_completa(texto: str) -> dict:
    texto_limpio = normalizar(texto)

    palabras_servicio = [
        "mechas", "queratina", "alisado", "coloración", "tratamiento", "brillo",
        "masdemont", "hidratar", "reparar", "cabello", "pelo", "tinte", "vegana"
    ]

    palabras_proceso = [
        "caja", "inventario", "cerrar", "cuadrar", "proceso", "tarea", "pedido", "stock"
    ]

    # 🧴 CONSULTAR PRODUCTO desde el diccionario (coincidencia parcial inteligente)
    for nombre_norm, nombre_original in PRODUCTOS_NOMBRES_NORMALIZADOS.items():
        if nombre_norm in texto_limpio:
            logging.info(f"[PRODUCTO] Detectado por coincidencia: {nombre_original}")
            return {
                "intencion": "consultar_producto",
                "producto": nombre_original,
                "atributo": extraer_duda_proceso(texto),
                "comentario": f"Detectado producto '{nombre_original}' desde JSON (coincidencia normalizada)",
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





