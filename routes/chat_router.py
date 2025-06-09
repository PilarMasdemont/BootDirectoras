from fastapi import APIRouter, Request
import logging
import re

from dispatcher import despachar_intencion
from extractores import (
    extraer_fecha_desde_texto,
    extraer_codsalon,
    extraer_codempleado,
    detectar_kpi,
)
from extractor_definicion_ratio import extraer_kpi
from memory import user_context

router = APIRouter()

@router.post("")
async def chat(request: Request):
    body = await request.json()
    mensaje = body.get("mensaje", "")
    codsalon = body.get("codsalon")
    ip_usuario = request.client.host

    logging.info(f"📥 Petición recibida: '{mensaje}' (salón: {codsalon})")

    # Extraer código de empleado y limpiar mensaje para fecha
    texto_limpio = mensaje
    codempleado = extraer_codempleado(mensaje)
    if codempleado:
        texto_limpio = re.sub(r"emplead[oa]\s*\d+", "", mensaje)
        texto_limpio = re.sub(r"\s{2,}", " ", texto_limpio).strip()

    # Extraer fecha
    fecha = extraer_fecha_desde_texto(texto_limpio)
    if not fecha or "no_valida" in str(fecha).lower():
        logging.warning(f"[FECHA] Inválida o ausente: {fecha}")
        fecha = ""
    else:
        logging.info(f"[FECHA] Extraída: {fecha}")

    # Extraer KPI
    kpi = extraer_kpi(mensaje) or detectar_kpi(mensaje)
    if kpi:
        logging.info(f"[KPI] Detectado: {kpi}")

    # Deducción de intención
    if fecha:
        intencion = "ratio_empleado" if codempleado else "ratio_dia"
    else:
        intencion = "kpi" if kpi else "general"
    logging.info(f"[INTENCION] Determinada: {intencion}")

    # Preparar sesión
    sesion = user_context[(ip_usuario, fecha)]
    sesion.update({"codsalon": codsalon, "codempleado": codempleado, "fecha": fecha, "kpi": kpi})

    # Llamar al dispatcher
    resultado = despachar_intencion(
        intencion=intencion,
        texto_usuario=mensaje,
        fecha=fecha,
        codsalon=codsalon,
        codempleado=codempleado,
        kpi=kpi,
        sesion=sesion
    )

    if resultado:
        logging.info("[RESPUESTA] Resultado generado exitosamente")
        return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}

    logging.info("[FLUJO] No se ejecutó ninguna función directa")
    return {"respuesta": "Estoy pensando cómo responderte mejor. Pronto te daré una respuesta."}
