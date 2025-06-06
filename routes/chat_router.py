
from fastapi import APIRouter, Request
import logging

from dispatcher import despachar_intencion
from funciones.intencion import clasificar_intencion
from extractores import (
    extraer_fecha_desde_texto,
    extraer_codsalon,
    extraer_codempleado,
    detectar_kpi,
)
from google_sheets_session import cargar_sesion

router = APIRouter()

@router.post("")  # o "/"
async def chat(request: Request):
    body = await request.json()
    mensaje_usuario = body.get("mensaje", "")
    ip_usuario = request.client.host

    logging.info(f"📥 Petición recibida: '{mensaje_usuario}'")

    intencion_info = clasificar_intencion(mensaje_usuario)
    intencion = intencion_info["intencion"]

    logging.info(f"[INTENCION] Detectada: {intencion} | Datos: {intencion_info}")

    fecha = extraer_fecha_desde_texto(mensaje_usuario)
    codsalon = extraer_codsalon(mensaje_usuario)
    codempleado = extraer_codempleado(mensaje_usuario)
    kpi = detectar_kpi(mensaje_usuario)

    logging.info(f"[FECHA] Extraída: {fecha}")
    logging.info(f"[SALON] Código detectado: {codsalon}")
    logging.info(f"[KPI] Detectado: {kpi}")
    logging.info(f"[EMPLEADO] Código detectado: {codempleado}")

    sesion = cargar_sesion(ip_usuario, fecha)

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
