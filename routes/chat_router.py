from fastapi import APIRouter, Request
import logging

from dispatcher import despachar_intencion
from funciones.intencion import clasificar_intencion
from funciones.intention_process import clasificar_intencion as clasificar_intencion_proceso
from funciones.consultar_proceso import consultar_proceso
from Archivos_estaticos.extractores_proceso import (
    extraer_nombre_proceso,
    extraer_duda_proceso
)
from extractores import (
    extraer_fecha_desde_texto,
    extraer_codsalon,
    extraer_codempleado,
    detectar_kpi,
)
from memory import user_context  # ← gestión de contexto

router = APIRouter()

@router.post("")
async def chat(request: Request):
    body = await request.json()
    mensaje_usuario = body.get("mensaje", "")
    ip_usuario = request.client.host

    logging.info(f"📥 Petición recibida: '{mensaje_usuario}'")

    # Paso 1: Detectar intención general (ratio, producto)
    intencion_info = clasificar_intencion(mensaje_usuario)

    # Paso 2: Si no se detecta nada claro, usar intención de proceso
    if intencion_info["intencion"] in ["general", "desconocida"]:
        intencion_info = clasificar_intencion_proceso(mensaje_usuario)

    intencion = intencion_info["intencion"]
    logging.info(f"[INTENCION] Detectada: {intencion} | Datos: {intencion_info}")

    # Si es una consulta de proceso, aplicar flujo especializado
    if intencion == "consultar_proceso":
        nombre_proceso = extraer_nombre_proceso(mensaje_usuario)
        atributo_duda = extraer_duda_proceso(mensaje_usuario)
        respuesta = consultar_proceso(nombre_proceso, atributo_duda)

        logging.info(f"[PROCESO] Proceso: {nombre_proceso} | Duda: {atributo_duda}")
        return {"respuesta": f"Hola, soy Mont Dirección.\n\n{respuesta}"}

    # Flujo normal de KPIs o productos
    fecha = extraer_fecha_desde_texto(mensaje_usuario)
    codsalon = body.get("codsalon") or extraer_codsalon(mensaje_usuario)
    codempleado = extraer_codempleado(mensaje_usuario)
    kpi = detectar_kpi(mensaje_usuario)

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

