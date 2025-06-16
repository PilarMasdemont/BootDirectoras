import re
import logging
from extractores import (
    extraer_codempleado,
    extraer_codsalon,
    extraer_fecha_desde_texto,
    detectar_kpi
)
from extractores_producto import extraer_nombre_producto
from funciones.intencion_total import clasificar_intencion_completa
from funciones.consultar_json_conocimiento import consultar_json_conocimiento
from funciones.consultar_proceso_con_chatgpt import consultar_proceso_chatgpt as consultar_proceso
from knowledge_base import base_conocimiento
from memory import obtener_contexto, actualizar_contexto  # ✅ memoria activa

logging.basicConfig(level=logging.INFO)

def manejar_peticion_chat(datos: dict) -> dict:
    mensaje_usuario = datos.get("mensaje", "")
    codsalon = datos.get("codsalon", "global")
    logging.info(f"📥 Petición recibida: '{mensaje_usuario}'")

    datos_intencion = clasificar_intencion_completa(mensaje_usuario)
    intencion = datos_intencion.get("intencion", "general")
    logging.info(f"[INTENCION] Detectada: {intencion} | Datos: {datos_intencion}")

    codempleado = extraer_codempleado(mensaje_usuario) if intencion == "empleado" else None
    texto_limpio = re.sub(r"emplead[oa]\s*\d+", "", mensaje_usuario).strip() if codempleado else mensaje_usuario
    fecha = extraer_fecha_desde_texto(texto_limpio)
    codsalon = codsalon or extraer_codsalon(mensaje_usuario)
    kpi = detectar_kpi(mensaje_usuario)

    if intencion == "consultar_proceso":
        # ✅ Recuperar el mejor contenido del JSON estructurado
        fragmento_base = consultar_json_conocimiento(mensaje_usuario, base_conocimiento)

        # ✅ Usar el fragmento como contexto para generar respuesta natural
        respuesta = consultar_proceso(
            proceso=mensaje_usuario,  # puede usarse como pregunta
            contexto=fragmento_base,
            atributo=None
        )

        return {
            "intencion": intencion,
            "respuesta": respuesta,
            "codsalon": codsalon,
            "fecha": fecha,
            "codempleado": codempleado
        }

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



