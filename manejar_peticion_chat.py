import re
from funciones.intencion import clasificar_intencion
from extractores import (
    extraer_fecha_desde_texto,
    extraer_codempleado,
    extraer_codsalon,
    detectar_kpi
)

def manejar_peticion_chat(mensaje_usuario: str) -> dict:
    # Paso 1: Clasificar la intención
    datos_intencion = clasificar_intencion(mensaje_usuario)
    intencion = datos_intencion.get("intencion", "general")

    # Paso 2: Preparar texto según intención
    if intencion == "empleado":
        codempleado = extraer_codempleado(mensaje_usuario)
        texto_limpio = re.sub(r"emplead[oa]\\s*\\d+", "", mensaje_usuario)
        texto_limpio = re.sub(r"\\s{2,}", " ", texto_limpio).strip()
    else:
        codempleado = None
        texto_limpio = mensaje_usuario

    # Paso 3: Extraer parámetros
    fecha = extraer_fecha_desde_texto(texto_limpio)
    codsalon = extraer_codsalon(mensaje_usuario)
    kpi = detectar_kpi(mensaje_usuario)

    # Paso 4: Retornar estructura con todos los datos necesarios
    return {
        "intencion": intencion,
        "tiene_fecha": datos_intencion.get("tiene_fecha", False),
        "codempleado": codempleado,
        "fecha": fecha,
        "codsalon": codsalon,
        "kpi": kpi
    }
