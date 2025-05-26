from .explicar_ratio_diario import explicar_ratio_diario
from .explicar_ratio_empleados import explicar_ratio_empleados
from .intencion import clasificar_intencion

def explicar_ratio(codsalon: str, fecha: str, mensaje_usuario: str) -> str:
    try:
        tipo = clasificar_intencion(mensaje_usuario)
        if tipo == "individual":
            return explicar_ratio_empleados(codsalon, fecha)
        else:
            return explicar_ratio_diario(codsalon, fecha)
    except Exception as e:
        return f"❌ Error al clasificar la intención del mensaje: {str(e)}"
