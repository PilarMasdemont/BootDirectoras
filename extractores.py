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

def extraer_fecha_desde_texto(texto: str, anio_por_defecto=2025):
    logger.info(f"[FECHA] Texto recibido para análisis: '{texto}'")
    texto = texto.lower()

    meses_es_en = {
        "enero": "january", "febrero": "february", "marzo": "march",
        "abril": "april", "mayo": "may", "junio": "june",
        "julio": "july", "agosto": "august", "septiembre": "september",
        "octubre": "october", "noviembre": "november", "diciembre": "december"
    }

    dias_semana = {
        "lunes": 0, "martes": 1, "miércoles": 2, "miercoles": 2,
        "jueves": 3, "viernes": 4, "sábado": 5, "sabado": 5, "domingo": 6
    }

    numeros_texto = {
        "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
        "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10
    }
    for palabra, numero in numeros_texto.items():
        texto = re.sub(rf"\b{palabra}\b", str(numero), texto)

    for es, en in meses_es_en.items():
        texto = texto.replace(es, en)

    hoy = datetime.today()

    if "hoy" in texto:
        fecha = hoy.strftime("%Y-%m-%d")
        logger.info(f"[FECHA] Detectado 'hoy': {fecha}")
        return fecha

    if "ayer" in texto:
        fecha = (hoy - timedelta(days=1)).strftime("%Y-%m-%d")
        logger.info(f"[FECHA] Detectado 'ayer': {fecha}")
        return fecha

    match = re.search(r"hace\s+(\d+)\s+d[ií]as?", texto)
    if match:
        dias = int(match.group(1))
        fecha = (hoy - timedelta(days=dias)).strftime("%Y-%m-%d")
        logger.info(f"[FECHA] Detectado 'hace X días': {fecha}")
        return fecha

    match = re.search(r"el\s+(lunes|martes|miércoles|miercoles|jueves|viernes|sábado|sabado|domingo)\s+pasado", texto)
    if match:
        dia_nombre = match.group(1)
        dia_target = dias_semana[dia_nombre]
        dias_diferencia = (hoy.weekday() - dia_target + 7) % 7 or 7
        fecha = (hoy - timedelta(days=dias_diferencia)).strftime("%Y-%m-%d")
        logger.info(f"[FECHA] Detectado 'el {dia_nombre} pasado': {fecha}")
        return fecha

    match = re.search(r"el\s+último\s+(lunes|martes|miércoles|miercoles|jueves|viernes|sábado|sabado|domingo)\s+de\s+(\w+)", texto)
    if match:
        dia_nombre = match.group(1)
        mes_nombre = match.group(2)
        try:
            mes = list(meses_es_en.keys()).index(mes_nombre) + 1
            anio = anio_por_defecto
            _, ultimo_dia = calendar.monthrange(anio, mes)
            for dia in range(ultimo_dia, 0, -1):
                fecha = datetime(anio, mes, dia)
                if fecha.weekday() == dias_semana[dia_nombre]:
                    resultado = fecha.strftime("%Y-%m-%d")
                    logger.info(f"[FECHA] Detectado 'último {dia_nombre} de {mes_nombre}': {resultado}")
                    return resultado
        except KeyError:
            logger.warning(f"[FECHA] Error al interpretar mes: {mes_nombre}")

    texto = re.sub(r"(emplead[oa]|trabajador[a]?)\s*\d+", "", texto)
    texto = re.sub(r"\s{2,}", " ", texto).strip()

    patron_fecha = re.search(r"\b(\d{1,2})\s+de\s+([a-zA-Z]+)(?:\s+de\s+(\d{4}))?\b", texto)
    if patron_fecha:
        dia, mes_str, anio = patron_fecha.groups()
        mes_str = mes_str.lower()
        if mes_str in meses_es_en:
            mes = list(meses_es_en.keys()).index(mes_str) + 1
            anio = int(anio) if anio else anio_por_defecto
            try:
                fecha = datetime(anio, mes, int(dia)).strftime("%Y-%m-%d")
                logger.info(f"[FECHA] Fecha explícita detectada: {fecha}")
                return fecha
            except Exception as e:
                logger.warning(f"[FECHA] Error al crear fecha explícita: {e}")

    try:
        fecha = parser.parse(texto, fuzzy=True, dayfirst=True)
        if not re.search(r"\b\d{4}\b", texto):
            fecha = fecha.replace(year=anio_por_defecto)
        fecha_str = fecha.strftime("%Y-%m-%d")
        logger.info(f"[FECHA] Fecha interpretada con parser: {fecha_str}")
        return fecha_str
    except Exception as e:
        logger.error(f"[FECHA] ❌ Error al interpretar la fecha: {e}")
        logger.debug(f"[FECHA] Resultado final: FECHA_NO_VALIDA ({type('FECHA_NO_VALIDA')})")
        return "FECHA_NO_VALIDA"

def extraer_codsalon(texto: str):
    texto = texto.lower()
    match = re.search(r"sal[oó]n\\s*(\\d+)", texto)
    if match:
        logger.info(f"[SALON] Código de salón extraído: {match.group(1)}")
        return match.group(1)
    logger.info("[SALON] No se detectó código de salón")
    return None
