# extractores.py
import re
import calendar
import logging
from datetime import datetime, timedelta
from dateutil import parser

logger = logging.getLogger(__name__)

def detectar_kpi(texto: str):
    texto = texto.lower()
    logger.info(f"[KPI] Texto recibido: '{texto}'")
    if "productividad" in texto:
        logger.info("[KPI] Detectado: productividad")
        return "productividad"
    elif "clientes nuevos" in texto or "nuevos clientes" in texto:
        logger.info("[KPI] Detectado: clientes_nuevos")
        return "clientes_nuevos"
    elif "servicio" in texto:
        logger.info("[KPI] Detectado: servicios")
        return "servicios"
    logger.info("[KPI] Ningún KPI detectado")
    return None

def extraer_codempleado(texto: str):
    texto = texto.lower()
    match = re.search(r"(emplead[oa]|trabajador[a]?)\s*(\d+)", texto)
    if match:
        logger.info(f"[EXTRACCION] Código de empleado extraído: {match.group(2)}")
        return match.group(2)
    logger.info("[EXTRACCION] No se detectó código de empleado")
    return None

def extraer_codcliente(texto: str):
    texto = texto.lower()
    match = re.search(r"cliente\s*(\d+)", texto)
    if match:
        logger.info(f"[EXTRACCION] Código de cliente extraído: {match.group(1)}")
        return match.group(1)
    logger.info("[EXTRACCION] No se detectó código de cliente")
    return None

def extraer_nombre_producto(texto: str):
    texto = texto.lower()
    match = re.search(r"producto\s+(\w+)", texto)
    if match:
        logger.info(f"[PRODUCTO] Producto detectado: {match.group(1)}")
        return match.group(1)
    logger.info("[PRODUCTO] No se detectó nombre de producto")
    return None

def extraer_tema(texto: str):
    texto = texto.lower()
    match = re.search(r"explica[rm]?\s+(?:el|la)?\s*(\w+(?:\s+\w+)?)", texto)
    if match:
        logger.info(f"[TEMA] Tema detectado: {match.group(1)}")
        return match.group(1)
    logger.info("[TEMA] No se detectó tema")
    return None

def extraer_mes_desde_texto(texto: str):
    texto = texto.lower()
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    for mes in meses:
        if mes in texto:
            logger.info(f"[MES] Mes detectado: {mes}")
            return mes
    logger.info("[MES] No se detectó mes")
    return None

# ... (resto del archivo sin cambios)
