import sys
import os


from fastapi import APIRouter, Request
import logging

from funciones.consultar_con_chatgpt import consultar_con_chatgpt
from funciones.intencion_total import clasificar_intencion_completa
from memory import obtener_contexto, actualizar_contexto
from dispatcher import despachar_intencion

router = APIRouter()

def formato_markdown(texto: str) -> str:
    texto = texto.replace("\ud83d\udd39", "-")  # viñetas unicode
    texto = texto.replace("\u2022", "-")        # viñetas estándar
    texto = texto.replace("\n\n", "\n")         # elimina dobles saltos
    return texto.strip()

@router.post("")
async def chat(request: Request):
    body = await request.json()
    mensaje_usuario = body.get("mensaje", "")
    ip_usuario = request.client.host

    logging.info(f"📥 Petición recibida: '{mensaje_usuario}'")

    # Paso 1: Clasificación de intención
    intencion_info = clasificar_intencion_completa(mensaje_usuario)
    intencion = intencion_info["intencion"]
    logging.info(f"[INTENCION] Detectada: {intencion} | Comentario: {intencion_info.get('comentario')}")

    codsalon = body.get("codsalon")
    contexto = obtener_contexto(codsalon)
    actualizar_contexto(codsalon, "intencion", intencion)

    # Paso 2: Si es una duda sobre productos o procesos, usar nuevo flujo
    if intencion in ["consultar_proceso", "consultar_producto"]:
        respuesta = consultar_con_chatgpt(mensaje_usuario)
        respuesta_markdown = formato_markdown(respuesta)

        return {
            "respuesta": f"**Hola, soy Mont Dirección.**\n\n{respuesta_markdown}"
        }

    # Paso 3: Otras intenciones (métricas, agenda, KPIs...) → flujo directo
    resultado = despachar_intencion(
        intencion=intencion,
        texto_usuario=mensaje_usuario,
        fecha=body.get("fecha"),
        codsalon=codsalon,
        codempleado=body.get("codempleado"),
        kpi=body.get("kpi"),
        sesion=contexto
    )

    if resultado:
        logging.info("[RESPUESTA] Generada correctamente desde función directa")
        resultado_final = formato_markdown(resultado)
        return {
            "respuesta": f"**Hola, soy Mont Dirección.**\n\n{resultado_final}"
        }

    return {
        "respuesta": "Estoy pensando cómo responderte mejor. Pronto te daré una respuesta."
    }







