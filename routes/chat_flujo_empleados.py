# handlers/chat_flujo_empleados.py
from funciones.explicar_ratio_empleados import explicar_ratio_empleados

def manejar_flujo_empleados(sesion: dict) -> str:
    """
    Continúa el flujo paso a paso de análisis por empleado.
    Incrementa el índice y actualiza el modo.
    """
    codsalon = sesion.get("codsalon")
    fecha = sesion.get("fecha")
    indice = sesion.get("indice_empleado", 0)

    if not codsalon or not fecha:
        return "No tengo suficiente información para continuar el análisis de empleados."

    resultado = explicar_ratio_empleados(codsalon, fecha, indice)

    if "Ya se han mostrado todos los empleados" not in resultado:
        sesion["indice_empleado"] = indice + 1
        sesion["modo"] = "empleados"
    else:
        sesion["modo"] = None
        sesion["indice_empleado"] = 0

    return resultado
