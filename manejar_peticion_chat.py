from funciones.intencion import clasificar_intencion
from extractores import extraer_codempleado, extraer_codsalon, extraer_fecha_desde_texto, detectar_kpi
from funciones.consultar_con_chatgpt import seleccionar_y_responder_con_documentos
import re
import logging

logging.basicConfig(level=logging.INFO)

def manejar_peticion_chat(datos: dict) -> dict:
    mensaje_usuario = datos.get("mensaje", "")
    logging.info(f"📥 Petición recibida: '{mensaje_usuario}'")

    # Paso 1: Clasificar la intención
    datos_intencion = clasificar_intencion(mensaje_usuario)
    intencion = datos_intencion.get("intencion", "desconocida")
    logging.info(f"[INTENCION] Detectada: {intencion} | Datos: {datos_intencion}")

    # Paso 2: Si es una intención de ratios
    if intencion in ["empleado", "empleados", "kpi", "general_con_kpi", "general"]:
        if intencion == "empleado":
            codempleado = extraer_codempleado(mensaje_usuario)
            logging.info(f"[EXTRACCION] Código de empleado detectado: {codempleado}")
            texto_limpio = re.sub(r"emplead[oa]\\s*\\d+", "", mensaje_usuario)
            texto_limpio = re.sub(r"\\s{2,}", " ", texto_limpio).strip()
        else:
            codempleado = None
            texto_limpio = mensaje_usuario

        logging.info(f"[LIMPIEZA] Texto para extracción de fecha: '{texto_limpio}'")
        fecha = extraer_fecha_desde_texto(texto_limpio)
        logging.info(f"[FECHA] Extraída: {fecha}")
        codsalon = datos.get("codsalon") or extraer_codsalon(mensaje_usuario)
        logging.info(f"[SALON] Código detectado: {codsalon}")
        kpi = detectar_kpi(mensaje_usuario)
        logging.info(f"[KPI] Detectado: {kpi}")

        return {
            "intencion": intencion,
            "tiene_fecha": datos_intencion.get("tiene_fecha", False),
            "codempleado": codempleado,
            "fecha": fecha,
            "codsalon": codsalon,
            "kpi": kpi
        }

    # Paso 3: Si no es ratio, consultar documentos estáticos
    respuesta_doc = seleccionar_y_responder_con_documentos(mensaje_usuario)
    if respuesta_doc:
        return {
            "respuesta": respuesta_doc,
            "intencion": "documento_estatico"
        }

    # Paso 4: No es ratio ni documento estático
    return {
        "respuesta": "Lo siento, no tengo información suficiente para responder a tu pregunta en este momento.",
        "intencion": "desconocida"
    }






