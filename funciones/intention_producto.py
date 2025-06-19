import re
import logging

logger = logging.getLogger(__name__)

def clasificar_intencion_producto(texto: str) -> dict:
    texto = texto.lower().strip()

    patrones_duda_producto = [
        r"para qué", r"beneficio", r"sirve", r"cómo se usa", r"ingredientes",
        r"composición", r"modo de uso", r"frecuencia", r"resultados", r"efectos"
    ]

    nombres_comunes = [
        "champú", "acondicionador", "spray", "crema", "mascarilla", "serum", "espuma", "aceite",
        "bond repair", "fibre clinix", "silhouette", "blondme", "session label"
    ]

    frases_comunes = [
        r"qué hace", r"cómo se aplica", r"qué contiene", r"modo de aplicación",
        r"dime sobre", r"info de", r"explica el producto"
    ]

    if any(re.search(patron, texto) for patron in patrones_duda_producto):
        return {
            "intencion": "consultar_producto",
            "comentario": "Consulta sobre un atributo de un producto"
        }

    if any(re.search(patron, texto) for patron in frases_comunes):
        return {
            "intencion": "consultar_producto",
            "comentario": "Frase típica de consulta de producto"
        }

    if any(nombre in texto for nombre in nombres_comunes):
        return {
            "intencion": "consultar_producto",
            "comentario": "Mención directa de un producto conocido"
        }

    if len(texto.split()) <= 2:
        return {
            "intencion": "desconocida",
            "comentario": "Mensaje muy corto para detectar intención"
        }

    return {
        "intencion": "desconocida",
        "comentario": "No se detecta intención clara sobre productos"
    }
