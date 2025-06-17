from funciones.intencion import clasificar_intencion as clasificar_general
from funciones.intention_process import clasificar_intencion as clasificar_proceso
from funciones.extractores_proceso import extraer_nombre_proceso, extraer_duda_proceso
from rapidfuzz import fuzz
import json
import os
import re

# 🧽 Utilidad para normalizar texto
def normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = re.sub(r"[^a-záéíóúüñ0-9\s]", "", texto)
    texto = re.sub(r"\b\d+ml\b", "", texto)  # elimina "200ml", "300ml", etc.
    return texto.strip()

# 📦 Cargar nombres de productos del JSON
PRODUCTOS_PATH = "Archivos_estaticos/productos_diccionario.json"
with open(PRODUCTOS_PATH, "r", encoding="utf-8") as f:
    PRODUCTOS_JSON = json.load(f)
    PRODUCTOS_NOMBRES = list(PRODUCTOS_JSON.keys())

def buscar_producto_fuzzy(texto_limpio: str) -> str:
    mejor_score = 0
    mejor_nombre = None

    for nombre in PRODUCTOS_NOMBRES:
        nombre_norm = normalizar(nombre)
        score = fuzz.partial_ratio(nombre_norm, texto_limpio)
        if score > mejor_score:
            mejor_score = score
            mejor_nombre = nombre

    return mejor_nombre if mejor_score >= 80 else None

def clasificar_intencion_completa(texto: str) -> dict:
    texto_limpio = normalizar(texto)

    palabras_servicio = [
        "mechas", "queratina", "alisado", "coloración", "tratamiento", "brillo",
        "masdemont", "hidratar", "reparar", "cabello", "pelo", "tinte", "vegana"
    ]

    palabras_proceso = [
        "caja", "inventario", "cerrar", "cuadrar", "proceso", "tarea", "pedido", "stock"
    ]

    # 🧴 CONSULTAR PRODUCTO usando búsqueda fuzzy
    producto_detectado = buscar_producto_fuzzy(texto_limpio)
    if producto_detectado:
        return {
            "intencion": "consultar_producto",
            "producto": producto_detectado,
            "atributo": extraer_duda_proceso(texto),
            "comentario": f"Detectado producto '{producto_detectado}' con fuzzy matching",
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

    # 🔄 Fallback específico de proceso
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







