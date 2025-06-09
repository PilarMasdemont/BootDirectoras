from funciones.intencion import clasificar_intencion
from extractores import extraer_codempleado, extraer_codsalon, extraer_fecha_desde_texto
from extractores_producto import extraer_nombre_producto
from extractor_definicion_ratio import extraer_kpi

import re
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

def manejar_peticion_chat(datos: dict) -> dict:
    mensaje_usuario = datos.get("mensaje", "")
    logging.info(f"📥 Petición recibida: '{mensaje_usuario}'")

    # Paso 1: Clasificar la intención
    datos_intencion = clasificar_intencion(mensaje_usuario)
    intencion = datos_intencion.get("intencion", "general")
    logging.info(f"[INTENCION] Detectada: {intencion} | Datos: {datos_intencion}")

    # Paso 2: Preparar texto según intención
    if intencion == "empleado":
        codempleado = extraer_codempleado(mensaje_usuario)
        logging.info(f"[EXTRACCION] Código de empleado detectado: {codempleado}")
        texto_limpio = re.sub(r"emplead[oa]\s*\d+", "", mensaje_usuario)
        texto_limpio = re.sub(r"\s{2,}", " ", texto_limpio).strip()
    else:
        codempleado = None
        texto_limpio = mensaje_usuario

    logging.info(f"[LIMPIEZA] Texto para extracción de fecha: '{texto_limpio}'")

    # Paso 3: Extraer parámetros
    anio_actual = datetime.now().year
    if intencion == "kpi":
        fecha = None
        logging.info("[FECHA] No se extrae fecha para intención 'kpi'")
    else:
        fecha = extraer_fecha_desde_texto(texto_limpio, anio_por_defecto=anio_actual)
        logging.info(f"[FECHA] Extraída: {fecha}")

    codsalon = datos.get("codsalon") or extraer_codsalon(mensaje_usuario)
    logging.info(f"[SALON] Código detectado: {codsalon}")

    kpi = extraer_kpi(mensaje_usuario) if intencion == "kpi" else None
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

    logging.info(f"[RESULTADO] Resultado ensamblado: {resultado}")

    return resultado











