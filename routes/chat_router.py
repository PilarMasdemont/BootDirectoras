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
from extractores_producto import extraer_nombre_producto
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

    # 🧠 Diagnóstico de clasificación
    logging.info(f"[INTENCION] Detectada: {intencion}")
    logging.info(f"[INFO] Clasificación completa: {intencion_info}")
    logging.info(f"[INFO] Producto detectado: {intencion_info.get('producto')}")
    logging.info(f"[INFO] Atributo detectado: {intencion_info.get('atributo')}")

    codsalon = body.get("codsalon") or extraer_codsalon(mensaje_usuario)
    fecha = extraer_fecha_desde_texto(mensaje_usuario)
    codempleado = extraer_codempleado(mensaje_usuario)
    kpi = detectar_kpi(mensaje_usuario)

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
        nombre_producto = intencion_info.get("producto")
        atributo_duda = intencion_info.get("atributo")

        if nombre_producto:
            actualizar_contexto(codsalon, "producto", nombre_producto)
        if atributo_duda:
            actualizar_contexto(codsalon, "atributo", atributo_duda)

        respuesta = consultar_producto_chatgpt(nombre_producto, atributo_duda)
        respuesta_markdown = formato_markdown(respuesta)

        return {
            "respuesta": f"**Hola, soy Mont Dirección.**\n\n{respuesta_markdown}"
        }

    # ✂️ SERVICIOS ESTÉTICOS / PRODUCTOS COSMÉTICOS
    if intencion == "explicar_producto":
        nombre_producto = extraer_nombre_producto(mensaje_usuario)
        if nombre_producto:
            logging.info(f"[PRODUCTO] Detectado por alias: {nombre_producto}")
            respuesta = consultar_producto_chatgpt(nombre_producto)
            respuesta_markdown = formato_markdown(respuesta)
            return {
                "respuesta": f"**Hola, soy Mont Dirección.**\n\n{respuesta_markdown}"
            }
        else:
            logging.info("[PRODUCTO] No se encontró producto por alias.")


    contexto = obtener_contexto(codsalon)

    # 🔁 RESET CONTEXTO si cambió la intención
    if intencion != contexto.get("intencion"):
        limpiar_contexto(codsalon)

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
        resultado_final = formato_markdown(resultado)
        return {"respuesta": f"**Hola, soy Mont Dirección.**\n\n{resultado_final}"}

    return {
        "respuesta": "Estoy pensando cómo responderte mejor. Pronto te daré una respuesta."
    }





