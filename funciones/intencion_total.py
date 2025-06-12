from funciones.intencion import clasificar_intencion as clasificar_general
from funciones.intention_process import clasificar_intencion as clasificar_proceso
from funciones.extractores_proceso import extraer_nombre_proceso, extraer_duda_proceso

def clasificar_intencion_completa(texto: str) -> dict:
    texto = texto.strip().lower()

    # Paso 1: Clasificación general
    resultado_general = clasificar_general(texto)
    intencion = resultado_general.get("intencion", "desconocida")

    # Si no se reconoce claramente, probar con procesos
    if intencion == "desconocida":
        resultado_proceso = clasificar_proceso(texto)
        intencion = resultado_proceso.get("intencion", intencion)
    else:
        resultado_proceso = {}

    resultado = {
        "intencion": intencion,
        "comentario": resultado_proceso.get("comentario") or resultado_general.get("comentario"),
        "tiene_fecha": any(p in texto for p in ["hoy", "ayer", "semana", "mes", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]),
    }

    if intencion == "consultar_proceso":
        proceso = extraer_nombre_proceso(texto)
        atributo = extraer_duda_proceso(texto)
        resultado["proceso"] = proceso
        resultado["atributo"] = atributo

    return resultado
