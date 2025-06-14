from funciones.extractores_proceso import (
    extraer_duda_proceso,
    extraer_nombre_proceso_desde_alias
)
from funciones.intention_process import es_consulta_proceso
from extractores import detectar_kpi, extraer_codempleado, extraer_codsalon, extraer_fecha_desde_texto
from extractores_producto import extraer_nombre_producto


def clasificar_intencion_completa(texto_usuario: str) -> dict:
    intencion = "desconocido"
    proceso = None
    producto = None
    kpi = None
    codempleado = None
    codsalon = None
    fecha = None

    if es_consulta_proceso(texto_usuario):
        intencion = "consultar_proceso"
        proceso = extraer_nombre_proceso_desde_alias(texto_usuario)
    elif detectar_kpi(texto_usuario):
        intencion = "consultar_kpi"
        kpi = detectar_kpi(texto_usuario)
        codempleado = extraer_codempleado(texto_usuario)
        codsalon = extraer_codsalon(texto_usuario)
        fecha_temp = extraer_fecha_desde_texto(texto_usuario)
        fecha = fecha_temp if fecha_temp != "FECHA_NO_VALIDA" else None
    elif extraer_nombre_producto(texto_usuario):
        intencion = "consultar_producto"
        producto = extraer_nombre_producto(texto_usuario)

    return {
        "intencion": intencion,
        "proceso": proceso,
        "producto": producto,
        "kpi": kpi,
        "codempleado": codempleado,
        "codsalon": codsalon,
        "fecha": fecha,
    }

