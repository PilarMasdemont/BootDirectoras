import re
import logging

logger = logging.getLogger(__name__)

def clasificar_intencion(texto: str) -> dict:
    texto = texto.lower().strip()
    logger.info(f"[CLASIFICADOR] Texto recibido: '{texto}'")

    # 1. ratio_empleado
    if re.search(r"(emplead[oa]|trabajador[a]?)\s*\d+.*\d{1,2}\s+de\s+\w+", texto):
        logger.info("[CLASIFICADOR] Intención detectada: ratio_empleado")
        return {
            "intencion": "ratio_empleado",
            "comentario": "Ratio de empleado en día específico"
        }

    # 2. ratio_dia
    if re.search(r"ratio.*\d{1,2}\s+de\s+\w+", texto):
        logger.info("[CLASIFICADOR] Intención detectada: ratio_dia")
        return {
            "intencion": "ratio_dia",
            "comentario": "Ratio general del día"
        }

    # 3. mes
    if re.search(r"(cómo va|como va|qué tal va|que tal va).*(este|el) mes", texto):
        logger.info("[CLASIFICADOR] Intención detectada: mes")
        return {
            "intencion": "mes",
            "comentario": "Consulta sobre rendimiento del mes"
        }

    # 4. cliente_dia
    if re.search(r"cliente\s+\w+.*\d{1,2}\s+de\s+\w+", texto):
        logger.info("[CLASIFICADOR] Intención detectada: cliente_dia")
        return {
            "intencion": "cliente_dia",
            "comentario": "Consulta sobre cliente específico en un día"
        }

    # 5. producto
    if re.search(r"producto|keratina|glatt|schwarzkopf|alisador|tratamiento", texto):
        logger.info("[CLASIFICADOR] Intención detectada: producto")
        return {
            "intencion": "producto",
            "comentario": "Consulta sobre producto"
        }

    # 6. explicacion
    if re.search(r"explica[rm]?\s+(el|la)?\s*(proceso|función|sistema|uso|planificación|gestión)", texto):
        logger.info("[CLASIFICADOR] Intención detectada: explicacion")
        return {
            "intencion": "explicacion",
            "comentario": "Petición de explicación temática"
        }

    # 7. argumento_venta
    if re.search(r"argumento[s]? de venta|cómo vender|como vender", texto):
        logger.info("[CLASIFICADOR] Intención detectada: argumento_venta")
        return {
            "intencion": "argumento_venta",
            "comentario": "Petición de argumento de venta"
        }

    logger.info("[CLASIFICADOR] Intención detectada: desconocida")
    return {
        "intencion": "desconocida",
        "comentario": "No se pudo clasificar"
    }
