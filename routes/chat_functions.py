# handlers/chat_functions.py
import json
import logging
from intenciones.explicar_ratio.ratio_diario import explicar_ratio_diario
from funciones.explicar_ratio_semanal import explicar_ratio_semanal
from funciones.explicar_ratio_mensual import explicar_ratio_mensual
from funciones.explicar_ratio_empleados import explicar_ratio_empleados
from intenciones.explicar_ratio.ratio_empleado import explicar_ratio_empleado_individual

logger = logging.getLogger(__name__)

def get_definiciones_funciones():
    return [
        {
            "name": "explicar_ratio_diario",
            "description": "Explica ratios diarios.",
            "parameters": {
                "type": "object",
                "properties": {
                    "codsalon": {"type": "string"},
                    "fecha": {"type": "string"}
                },
                "required": ["codsalon", "fecha"]
            }
        },
        {
            "name": "explicar_ratio_semanal",
            "description": "Explica ratios semanales.",
            "parameters": {
                "type": "object",
                "properties": {
                    "codsalon": {"type": "string"},
                    "nsemana": {"type": "integer"}
                },
                "required": ["codsalon", "nsemana"]
            }
        },
        {
            "name": "explicar_ratio_mensual",
            "description": "Explica ratios mensuales.",
            "parameters": {
                "type": "object",
                "properties": {
                    "codsalon": {"type": "string"},
                    "mes": {"type": "string"},
                    "codempleado": {"type": "string"}
                },
                "required": ["codsalon", "mes", "codempleado"]
            }
        },
        {
            "name": "explicar_ratio_empleados",
            "description": "Explica ratios de cada trabajador de forma progresiva.",
            "parameters": {
                "type": "object",
                "properties": {
                    "codsalon": {"type": "string"},
                    "fecha": {"type": "string"}
                },
                "required": ["codsalon", "fecha"]
            }
        },
        {
            "name": "explicar_ratio_empleado_individual",
            "description": "Explica ratio de un empleado individual.",
            "parameters": {
                "type": "object",
                "properties": {
                    "codsalon": {"type": "string"},
                    "fecha": {"type": "string"},
                    "codempleado": {"type": "string"}
                },
                "required": ["codsalon", "fecha", "codempleado"]
            }
        },
        {
            "name": "definir_kpi",
            "description": "Devuelve la definición de un KPI concreto.",
            "parameters": {
                "type": "object",
                "properties": {
                    "kpi": {"type": "string"}
                },
                "required": ["kpi"]
            }
        }
    ]

def resolver(function_call, sesion: dict) -> str:
    nombre_funcion = function_call.name
    argumentos = json.loads(function_call.arguments)
    logger.info(f"[CALL] Resolviendo: {nombre_funcion} con argumentos iniciales: {argumentos}")

    if "fecha" in sesion:
        argumentos["fecha"] = sesion["fecha"]
        logger.info(f"[CALL] Fecha reforzada desde sesión: {argumentos['fecha']}")

    try:
        if nombre_funcion == "explicar_ratio_diario":
            return explicar_ratio_diario(**argumentos)
        elif nombre_funcion == "explicar_ratio_semanal":
            return explicar_ratio_semanal(**argumentos)
        elif nombre_funcion == "explicar_ratio_mensual":
            return explicar_ratio_mensual(**argumentos)
        elif nombre_funcion == "explicar_ratio_empleado_individual":
            return explicar_ratio_empleado_individual(**argumentos)
        elif nombre_funcion == "explicar_ratio_empleados":
            indice = sesion.get("indice_empleado", 0)
            logger.info(f"[CALL] Índice empleado actual: {indice}")
            resultado = explicar_ratio_empleados(
                codsalon=argumentos["codsalon"],
                fecha=argumentos["fecha"],
                indice=indice
            )
            sesion["indice_empleado"] = indice + 1
            sesion["modo"] = "empleados"
            return resultado
        elif nombre_funcion == "definir_kpi":
            from intenciones.explicar_kpi import definicion_kpi
            return definicion_kpi(argumentos["kpi"])
        else:
            logger.error(f"[ERROR] Función no reconocida: {nombre_funcion}")
            raise ValueError("Función no reconocida")
    except Exception as e:
        logger.error(f"[ERROR] Fallo al resolver función {nombre_funcion}: {e}")
        raise

