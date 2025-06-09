from fastapi import APIRouter, Request
import logging

from dispatcher import despachar_intencion
from funciones.intencion import clasificar_intencion
from extractores import (
    extraer_fecha_desde_texto,
    extraer_codsalon,
    extraer_codempleado,
)
from extractor_definicion_ratio import extraer_kpi
from memory import user_context

router = APIRouter()

REQUISITOS = {
    "ratio_dia": ["fecha", "codsalon"],
    "ratio_empleado": ["fecha", "codsalon", "codempleado"],
    "empleado": ["fecha", "codsalon", "codempleado"],
    "general": ["codsalon"],
    "kpi": ["kpi"]
}

@router.post("")
async def chat(request: Request):
    body = await request.json()
    mensaje_usuario = body.get("mensaje", "")
    ip_usuario = request.client.host

    logging.info(f"📥 Petición recibida: '{mensaje_usuario}'")

    intencion_info = clasificar_intencion(mensaje_usuario)
    intencion = intencion_info["intencion"]
    user_context[(ip_usuario, body.get("fecha") or "")]["intencion"] = intencion

    logging.info(f"[INTENCION] Detectada: {intencion} | Datos: {intencion_info}")

    fecha = extraer_fecha_desde_texto(mensaje_usuario)
    if not fecha or "no_valida" in str(fecha).lower():
        logging.warning(f"[FECHA] Fecha inválida detectada: {fecha}")
        fecha = ""

    codsalon = body.get("codsalon") or extraer_codsalon(mensaje_usuario)
    codempleado = extraer_codempleado(mensaje_usuario)
    kpi = extraer_kpi(mensaje_usuario)

    logging.info(f"[FECHA] Extraída: {fecha}")
    logging.info(f"[SALON] Código detectado: {codsalon}")
    logging.info(f"[KPI] Detectado: {kpi}")
    logging.info(f"[EMPLEADO] Código detectado: {codempleado}")

    sesion = user_context[(ip_usuario, fecha or "")]

    sesion["codsalon"] = codsalon
    sesion["codempleado"] = codempleado
    sesion["kpi"] = kpi
    sesion["fecha"] = fecha

    faltantes = [campo for campo in REQUISITOS.get(intencion, []) if not locals().get(campo)]
    if faltantes:
        return {"respuesta": f"Necesito que me indiques: {', '.join(faltantes)} para poder responder correctamente."}

    resultado = despachar_intencion(
        intencion=intencion,
        texto_usuario=mensaje_usuario,
        fecha=fecha,
        codsalon=codsalon,
        codempleado=codempleado,
        kpi=kpi,
        sesion=sesion
    )

    if resultado:
        logging.info("[RESPUESTA] Resultado generado exitosamente desde función directa")
        return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}

    logging.info("[FLUJO] No se ejecutó ninguna función directa")
    return {"respuesta": "Estoy pensando cómo responderte mejor. Pronto te daré una respuesta."}


