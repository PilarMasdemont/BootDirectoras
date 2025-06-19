from fastapi import APIRouter, Request
import logging

from funciones.intencion_total import clasificar_intencion_completa
from funciones.consultar_proceso_con_chatgpt import consultar_proceso_chatgpt as consultar_proceso
from funciones.consultar_producto_con_chatgpt import consultar_producto_chatgpt
from funciones.extractores_proceso import (
    extraer_nombre_proceso,
    extraer_duda_proceso
)
from extractores import (
    extraer_fecha_desde_texto,
    extraer_codsalon,
    extraer_codempleado,
    detectar_kpi,
)
from funciones.extractores_producto import extraer_nombre_producto
from memory import obtener_contexto, actualizar_contexto, limpiar_contexto
from dispatcher import despachar_intencion

router = APIRouter()

def formato_markdown(texto: str) -> str:
    texto = texto.replace("🔹", "-")  # conviértelo a viñetas tipo lista
    texto = texto.replace("•", "-")   # viñetas estándar
    texto = texto.replace("\n\n", "\n")  # evita dobles saltos
    return texto.strip()

@router.post("")
async def chat(request: Request):
    body = await request.json()
    mensaje_usuario = body.get("mensaje", "")
    ip_usuario = request.client.host

    logging.info(f"📥 Petición recibida: '{mensaje_usuario}'")

    intencion_info = clasificar_intencion_completa(mensaje_usuario)
    intencion = intencion_info["intencion"]

    logging.info(f"[INTENCION] Detectada: {intencion}")
    logging.info(f"[INFO] Clasificación completa: {intencion_info}")
    logging.info(f"[INFO] Producto detectado: {intencion_info.get('producto')}")
    logging.info(f"[INFO] Atributo detectado: {intencion_info.get('atributo')}")

    codsalon = body.get("codsalon") or extraer_codsalon(mensaje_usuario)
    fecha = extraer_fecha_desde_texto(mensaje_usuario)
    codempleado = extraer_codempleado(mensaje_usuario)
    kpi = detectar_kpi(mensaje_usuario)

    # ⚠️ VALIDACIÓN DE FECHA
    if not fecha:
        logging.warning("[FECHA] No se detectó una fecha válida. Se omitirá.")
        if intencion in ["explicar_ratio_diario", "explicar_ratio_empleados", "explicar_ratio_empleado_individual"]:
            return {
                "respuesta": "**Hola, soy Mont Dirección.**\n\n❓ No logré identificar la fecha que mencionaste. ¿Podrías reformular la frase con una fecha clara?"
            }
    else:
        logging.info(f"[FECHA] Extraída: {fecha}")

    logging.info(f"[SALON] Código detectado: {codsalon}")
    logging.info(f"[KPI] Detectado: {kpi}")
    logging.info(f"[EMPLEADO] Código detectado: {codempleado}")

    # 🧾 CONSULTAR PROCESO
    if intencion == "consultar_proceso":
        nombre_proceso = intencion_info.get("proceso") or extraer_nombre_proceso(mensaje_usuario)
        atributo_duda = intencion_info.get("atributo") or extraer_duda_proceso(mensaje_usuario)

        contexto = obtener_contexto(codsalon)
        if not nombre_proceso and contexto.get("proceso"):
            nombre_proceso = contexto["proceso"]
        if not atributo_duda and contexto.get("atributo"):
            atributo_duda = contexto["atributo"]

        if nombre_proceso:
            actualizar_contexto(codsalon, "proceso", nombre_proceso)
        if atributo_duda:
            actualizar_contexto(codsalon, "atributo", atributo_duda)

        respuesta = consultar_proceso(nombre_proceso, mensaje_usuario)
        respuesta_markdown = formato_markdown(respuesta)

        return {
            "respuesta": f"**Hola, soy Mont Dirección.**\n\n{respuesta_markdown}"
        }

    # 🧴 CONSULTAR PRODUCTO
    if intencion == "consultar_producto":
        producto = intencion_info.get("producto") or extraer_nombre_producto(mensaje_usuario)
        if producto:
            actualizar_contexto(codsalon, "producto", producto)

        respuesta = consultar_producto_chatgpt(producto, mensaje_usuario)
        respuesta_markdown = formato_markdown(respuesta)

        return {
            "respuesta": f"**Hola, soy Mont Dirección.**\n\n{respuesta_markdown}"
        }

    # 🧠 CUALQUIER OTRA INTENCIÓN
    sesion = {"ip": ip_usuario}
    argumentos = {
        "intencion": intencion,
        "texto_usuario": mensaje_usuario,
        "codsalon": codsalon,
        "codempleado": codempleado,
        "kpi": kpi,
        "sesion": sesion
    }

    if fecha:
        argumentos["fecha"] = fecha

    respuesta = despachar_intencion(**argumentos)

    return {
        "respuesta": f"**Hola, soy Mont Dirección.**\n\n{formato_markdown(respuesta)}"
    }







