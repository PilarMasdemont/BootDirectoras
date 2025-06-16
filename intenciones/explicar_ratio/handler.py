# intenciones/explicar_ratio/handler.py

import logging
from .ratio_diario import explicar_ratio_diario
from .ratio_empleado import explicar_ratio_empleado_individual

logger = logging.getLogger(__name__)

def manejar_explicacion_diaria(codsalon: str, fecha: str) -> str:
    if fecha == "FECHA_NO_VALIDA":
        return "No entendí bien la fecha que mencionaste. ¿Puedes repetirla con más claridad?"
    
    logger.info(f"[HANDLER] Ejecutando explicación diaria para salón {codsalon} en fecha {fecha}")
    return explicar_ratio_diario(codsalon=codsalon, fecha=fecha)


def manejar_explicacion_empleado(codsalon: str, fecha: str, codempleado: str) -> str:
    if fecha == "FECHA_NO_VALIDA":
        return "No entendí bien la fecha que mencionaste. ¿Puedes repetirla con más claridad?"
    
    logger.info(f"[HANDLER] Ejecutando explicación de empleado {codempleado} para salón {codsalon} en fecha {fecha}")
    return explicar_ratio_empleado_individual(codsalon=codsalon, fecha=fecha, codempleado=codempleado)
