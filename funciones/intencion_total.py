from funciones.intencion import clasificar_intencion as clasificar_general
from funciones.intention_process import clasificar_intencion as clasificar_proceso
from funciones.extractores_proceso import extraer_nombre_proceso, extraer_duda_proceso

def clasificar_intencion_completa(texto: str) -> dict:
    texto = texto.strip().lower()

    # Paso 1: Primero intentamos clasificar como proceso
    resultado_proceso = clasificar_proceso(texto)
    if resultado_proceso.get("intencion") == "consultar_proceso":
        return {
            "intencion": "consultar_proceso",
            "comentario": resultado_proceso.get("comentario"),
            "proceso": extraer_nombre_proceso(texto),
            "atributo": extraer_duda_proceso(texto),
            "tiene_fecha": False
        }

    # Paso 2: Si no es proceso, intentamos clasificación general
    resultado_general = clasificar_general(texto)

    # Validación especial para evitar errores de fechas en preguntas NO relacionadas con ratios
    palabras_clave_ratio = ["ratio", "rendimiento", "productividad"]
    intencion_detectada = resultado_general.get("intencion", "desconocida")
    
    if any(p in texto for p in palabras_clave_ratio):
        tiene_fecha = any(p in texto for p in ["hoy", "ayer", "semana", "mes", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"])
    else:
        tiene_fecha = False  # Evitamos que dispare funciones que requieren fecha

    return {
        "intencion": intencion_detectada,
        "comentario": resultado_general.get("comentario"),
        "tiene_fecha": tiene_fecha
    }

