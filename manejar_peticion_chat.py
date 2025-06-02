from funciones.intencion import clasificar_intencion
from extractores import extraer_codempleado, extraer_codsalon, extraer_fecha_desde_texto, detectar_kpi
from extractores_producto import extraer_nombre_producto
import re
import logging

logging.basicConfig(level=logging.INFO)

def manejar_peticion_chat(datos: dict) -> dict:
    mensaje_usuario = datos.get("mensaje", "")

    # Paso 1: Clasificar la intención
    datos_intencion = clasificar_intencion(mensaje_usuario)
    intencion = datos_intencion.get("intencion", "general")
    logging.info(f"[INTENCION] Detectada: {intencion} | Datos: {datos_intencion}")

    # Paso 2: Preparar texto según intención
    if intencion == "empleado":
        codempleado = extraer_codempleado(mensaje_usuario)
        texto_limpio = re.sub(r"emplead[oa]\s*\d+", "", mensaje_usuario)
        texto_limpio = re.sub(r"\s{2,}", " ", texto_limpio).strip()
    else:
        codempleado = None
        texto_limpio = mensaje_usuario

    logging.info(f"[LIMPIEZA] Texto para extracción de fecha: '{texto_limpio}'")

    # Paso 3: Extraer parámetros
    if intencion == "explicar_producto":
        fecha = "NO_NECESARIA"
    else:
        try:
            fecha = extraer_fecha_desde_texto(texto_limpio)
        except Exception as e:
            fecha = "FECHA_NO_VALIDA"
            logging.error(f"❌ Error al interpretar la fecha en el texto '{texto_limpio}': {e}")

    logging.info(f"[FECHA] Extraída: {fecha}")

    codsalon = datos.get("codsalon") or extraer_codsalon(mensaje_usuario)
    kpi = detectar_kpi(mensaje_usuario)

    # Paso 4: Preparar retorno
    resultado = {
        "intencion": intencion,
        "tiene_fecha": datos_intencion.get("tiene_fecha", False),
        "codempleado": codempleado,
        "fecha": fecha,
        "codsalon": codsalon,
        "kpi": kpi
    }

    # ✅ Producto: extraer nombre usando extractor específico
    if intencion == "explicar_producto":
        resultado["nombre_producto"] = extraer_nombre_producto(mensaje_usuario)
        logging.info(f"[PRODUCTO] Extraído del mensaje: {resultado['nombre_producto']}")

    return resultado

