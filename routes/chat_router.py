from fastapi import APIRouter, Request
import logging

from dispatcher import despachar_intencion
from extractores import (
    extraer_fecha_desde_texto,
    extraer_codsalon,
    extraer_codempleado,
    detectar_kpi,
)
from memory import user_context

router = APIRouter()

@router.post("")
async def chat(request: Request):
    body = await request.json()
    mensaje_usuario = body.get("mensaje", "")
    ip_usuario = request.client.host

    logging.info(f"📥 Petición recibida: '{mensaje_usuario}'")

    fecha = extraer_fecha_desde_texto(mensaje_usuario)
    if not fecha or "no_valida" in str(fecha).lower():
        fecha = ""
        logging.warning(f"[FECHA] Fecha inválida o ausente: {fecha}")

    codsalon = body.get("codsalon")  # mantener solo lo que viene del frontend
    codempleado = extraer_codempleado(mensaje_usuario)
    kpi = detectar_kpi(mensaje_usuario)

    # Deducción explícita de intención
    if fecha:
        if codempleado:
            intencion = "ratio_empleado"
        else:
            intencion = "ratio_dia"
    else:
        if kpi:
            intencion = "kpi"
        else:
            intencion = "general"

    logging.info(f"[INTENCION] Determinada: {intencion}")
    logging.info(f"[FECHA] Extraída: {fecha}")
    logging.info(f"[SALON] Código detectado: {codsalon}")
    logging.info(f"[KPI] Detectado: {kpi}")
    logging.info(f"[EMPLEADO] Código detectado: {codempleado}")

    sesion = user_context[(ip_usuario, fecha)]
    sesion["codsalon"] = codsalon
    sesion["codempleado"] = codempleado
    sesion["kpi"] = kpi
    sesion["fecha"] = fecha

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



