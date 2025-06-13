from fastapi import APIRouter, Request
import logging

from funciones.intencion_total import clasificar_intencion_completa
from funciones.consultar_proceso_con_chatgpt import consultar_proceso_chatgpt as consultar_proceso
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
from extractores_producto import extraer_nombre_producto
from memory import obtener_contexto, actualizar_contexto
from dispatcher import despachar_intencion

router = APIRouter()

def formato_html(texto: str) -> str:
    # 🔧 Formato visual para HTML: negritas, viñetas, saltos de línea
    texto = texto.replace("**", "<b>").replace("</b><b>", "")
    texto = texto.replace("🔹", "•")
    texto = texto.replace("\n\n", "<br><br>")
    texto = texto.replace("\n", "<br>")
    return texto

@router.post("")
async def chat(request: Request):
    body = await request.json()
    mensaje_usuario = body.get("mensaje", "")
    ip_usuario = request.client.host

    logging.info(f"📥 Petición recibida: '{mensaje_usuario}'")

    intencion_info = clasificar_intencion_completa(mensaje_usuario)
    intencion = intencion_info["intencion"]
    logging.info(f"[INTENCION] Detectada: {intencion} | Comentario: {intencion_info.get('comentario')}")

    codsalon = body.get("codsalon") or extraer_codsalon(mensaje_usuario)
    fecha = extraer_fecha_desde_texto(mensaje_usuario)
    codempleado = extraer_codempleado(mensaje_usuario)
    kpi = detectar_kpi(mensaje_usuario)

    logging.info(f"[FECHA] Extraída: {fecha}")
    logging.info(f"[SALON] Código detectado: {codsalon}")
    logging.info(f"[KPI] Detectado: {kpi}")
    logging.info(f"[EMPLEADO] Código detectado: {codempleado}")

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

        # ✅ Enviamos la pregunta completa, no solo el atributo
        respuesta = consultar_proceso(nombre_proceso, mensaje_usuario)
        respuesta_html = formato_html(respuesta)

        return {
            "respuesta": f"<p><b>Hola, soy Mont Dirección.</b></p><br>{respuesta_html}"
        }

    if intencion == "explicar_producto":
        nombre_producto = extraer_nombre_producto(mensaje_usuario)
        logging.info(f"[PRODUCTO] Detectado: {nombre_producto}")

    contexto = obtener_contexto(codsalon)
    actualizar_contexto(codsalon, "codsalon", codsalon)
    actualizar_contexto(codsalon, "fecha", fecha)
    actualizar_contexto(codsalon, "codempleado", codempleado)
    actualizar_contexto(codsalon, "kpi", kpi)
    actualizar_contexto(codsalon, "intencion", intencion)

    resultado = despachar_intencion(
        intencion=intencion,
        texto_usuario=mensaje_usuario,
        fecha=fecha,
        codsalon=codsalon,
        codempleado=codempleado,
        kpi=kpi,
        sesion=contexto
    )

    if resultado:
        logging.info("[RESPUESTA] Generada correctamente desde función directa")
        respuesta_html = formato_html(resultado)
        return {
            "respuesta": f"<p><b>Hola, soy Mont Dirección.</b></p><br>{respuesta_html}"
        }

    return {
        "respuesta": "<p><b>Estoy pensando cómo responderte mejor.</b></p><br>Pronto te daré una respuesta."
    }




