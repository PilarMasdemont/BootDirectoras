from .explicar_ratio_diario import explicar_ratio_diario
from .explicar_ratio_empleados import explicar_ratio_empleados
from .explicar_ratio_empleado_individual import explicar_ratio_empleado_individual
from .intencion import clasificar_intencion
import re

def extraer_codempleado(texto: str):
    match = re.search(r"empleado\s*(\d+)", texto.lower())
    if match:
        return match.group(1)
    return None

def explicar_ratio(codsalon: str, fecha: str, mensaje_usuario: str) -> str:
    try:
        mensaje = mensaje_usuario.lower()
        codempleado = extraer_codempleado(mensaje)

        if codempleado:
            return explicar_ratio_empleado_individual(codsalon, fecha, codempleado)

        tipo = clasificar_intencion(mensaje_usuario)

        if tipo == "individual":
            return explicar_ratio_empleados(codsalon, fecha)

        return explicar_ratio_diario(codsalon, fecha)

    except Exception as e:
        return f"❌ Error al clasificar la intención del mensaje: {str(e)}"

