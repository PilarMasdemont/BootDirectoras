from funciones.intencion import clasificar_intencion
from extractores import extraer_codempleado, extraer_codsalon, extraer_fecha_desde_texto, detectar_kpi
from extractores_producto import extraer_nombre_producto
import re
import logging
from extractor_definicion_ratio import extraer_kpi

logging.basicConfig(level=logging.INFO)

def manejar_peticion_chat(datos: dict) -> dict:
    mensaje_usuario = datos.get("mensaje", "")
    logging.info(f"📥 Petición recibida: '{mensaje_usuario}'")

    datos_intencion = clasificar_intencion(mensaje_usuario)
    intencion = datos_intencion.get("intencion", "general")
    logging.info(f"[INTENCION] Detectada: {intencion} | Datos: {datos_intencion}")

    if intencion == "empleado":
        codempleado = extraer_codempleado(mensaje_usuario)
        logging.info(f"[EXTRACCION] Código de empleado detectado: {codempleado}")
        texto_limpio = re.sub(r"emplead[oa]\s*\d+", "", mensaje_usuario)
        texto_limpio = re.sub(r"\s{2,}", " ", texto_limpio).strip()
    else:
        codempleado = None
        texto_limpio = mensaje_usuario

    logging.info(f"[LIMPIEZA] Texto para extracción de fecha: '{texto_limpio}'")

    fecha = extraer_fecha_desde_texto(texto_limpio)
    logging.info(f"[DEBUG] Valor bruto de fecha extraída: {fecha} tipo: {type(fecha)}")
    if not fecha or "no_valida" in str(fecha).lower():
        logging.warning(f"[FECHA] Fecha inválida detectada: {fecha}")
        fecha = ""

    logging.info(f"[FECHA] Extraída: {fecha}")

    codsalon = datos.get("codsalon") or extraer_codsalon(mensaje_usuario)
    logging.info(f"[SALON] Código detectado: {codsalon}")

    kpi = detectar_kpi(mensaje_usuario)
    logging.info(f"[KPI] Detectado: {kpi}")

    resultado = {
        "intencion": intencion,
        "tiene_fecha": datos_intencion.get("tiene_fecha", False),
        "codempleado": codempleado,
        "fecha": fecha,
        "codsalon": codsalon,
        "kpi": kpi
    }

    if intencion == "explicar_producto":
        resultado["nombre_producto"] = extraer_nombre_producto(mensaje_usuario)
        logging.info(f"[PRODUCTO] Detectado: {resultado['nombre_producto']}")

    return resultado




