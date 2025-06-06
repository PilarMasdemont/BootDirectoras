# intenciones/explicar_ratio/handler.py

import logging
from .ratio_diario import explicar_ratio_diario
from .ratio_empleado import explicar_ratio_empleado_individual

logger = logging.getLogger(__name__)

# Este archivo actualmente solo importa funciones. No tiene lógica ejecutable
de momento.
# Para añadir logging útil, deberías implementar aquí funciones que hagan uso de esas importaciones
y dejen trazabilidad de cómo y cuándo se llaman.

# Ejemplo (si se amplía en el futuro):
# def manejar_explicacion_diaria(codsalon, fecha):
#     logger.info(f"[HANDLER] Ejecutando explicación diaria para salón {codsalon} en fecha {fecha}")
#     return explicar_ratio_diario(codsalon=codsalon, fecha=fecha)
