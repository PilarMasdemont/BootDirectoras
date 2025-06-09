from funciones.intencion import clasificar_intencion
from extractores import extraer_codempleado, extraer_fecha_desde_texto, extraer_codsalon, detectar_kpi
from extractor_definicion_ratio import extraer_kpi
from extractores_producto import extraer_nombre_producto
import re
import logging

logging.basicConfig(level=logging.INFO)

def manejar_peticion_chat(datos: dict) -> dict:
    mensaje = datos.get("mensaje", "")
    codsalon = datos.get("codsalon")
    logging.info(f"📥 Petición recibida: '{mensaje}' (salón: {codsalon})")

    # Extraer código de empleado y limpiar texto
    texto_limpio = mensaje
    codempleado = extraer_codempleado(mensaje)
    if codempleado:
        texto_limpio = re.sub(r"emplead[oa]\s*\d+", "", mensaje)
        texto_limpio = re.sub(r"\s{2,}", " ", texto_limpio).strip()

    # Extraer fecha
    fecha = extraer_fecha_desde_texto(texto_limpio)
    if not fecha or "no_valida" in str(fecha).lower():
        logging.warning(f"[FECHA] Inválida o ausente: {fecha}")
        fecha = None
    else:
        logging.info(f"[FECHA] Extraída: {fecha}")

    # Extraer KPI
    kpi = extraer_kpi(mensaje) or detectar_kpi(mensaje)
    if kpi:
        logging.info(f"[KPI] Detectado: {kpi}")

    # Determinar intención según fecha y empleado
    if fecha:
        if codempleado:
            intencion = "ratio_empleado"
        else:
            intencion = "ratio_dia"
    elif kpi:
        intencion = "kpi"
    else:
        intencion = "general"
    logging.info(f"[INTENCION] Asignada: {intencion}")

    resultado = {
        "intencion": intencion,
        "fecha": fecha,
        "codsalon": codsalon,
        "codempleado": codempleado,
        "kpi": kpi
    }

    # Definición de producto (sin fecha)
    if intencion == "explicar_producto":
        nombre_producto = extraer_nombre_producto(mensaje)
        logging.info(f"[PRODUCTO] Detectado: {nombre_producto}")
        resultado["nombre_producto"] = nombre_producto

    return resultado

