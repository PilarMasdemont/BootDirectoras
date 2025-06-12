from fastapi import APIRouter, Request
import logging

from funciones.intencion_total import clasificar_intencion_completa
from funciones.consultar_proceso import consultar_proceso
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
from memory import user_context
from dispatcher import despachar_intencion

router = APIRouter()

@router.post("")
async def chat(request: Request):
    body = await request.json()
    mensaje_usuario = body.get("mensaje", "")
    ip_usuario = request.client.host

    logging.info(f"📥 Petición recibida: '{mensaje_usuario}'")

    # Clasificación combinada (KPI, Producto, Proceso)
    intencion_info = clasificar_intencion_completa(mensaje_usuario)
    intencion = intencion_info["intencion"]
    logging.info(f"[INTENCION] Detectada: {intencion} | Comentario: {intencion_info.get('comentario')}")

    # Si la intención es proceso, ejecuta directamente ese flujo
    if intencion == "consultar_proceso":
        nombre_proceso = extraer_nombre_proceso(mensaje_usuario)
        atributo_duda = extraer_duda_proceso(mensaje_usuario)
        respuesta = consultar_proceso(nombre_proceso, atributo_duda)

        logging.info(f"[PROCESO] Proceso detectado: {nombre_proceso} | Atributo: {atributo_duda}")
        return {"respuesta": f"Hola, soy Mont Dirección.\n\n{respuesta}"}

    # Si es sobre productos
    if intencion == "explicar_producto":
        nombre_producto = extraer_nombre_producto(mensaje_usuario)
        logging.info(f"[PRODUCTO] Detectado: {nombre_producto}")

    # Flujo KPI / Producto (extraer contexto)
    fecha = extraer_fecha_desde_texto(mensaje_usuario)
    codsalon = body.get("codsalon") or extraer_codsalon(mensaje_usuario)
    codempleado = extraer_codempleado(mensaje_usuario)
    kpi = detectar_kpi(mensaje_usuario)

    logging.info(f"[FECHA] Extraída: {fecha}")
    logging.info(f"[SALON] Código detectado: {codsalon}")
    logging.info(f"[KPI] Detectado: {kpi}")
    logging.info(f"[EMPLEADO] Código detectado: {codempleado}")

    # Guardar contexto en memoria
    sesion = user_context[(ip_usuario, fecha)]
    sesion["codsalon"] = codsalon
    sesion["codempleado"] = codempleado
    sesion["kpi"] = kpi
    sesion["fecha"] = fecha
    sesion["intencion"] = intencion

    # Despachar lógica si hay función asociada
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
        logging.info("[RESPUESTA] Generada correctamente desde función directa")
        return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}

    logging.info("[FLUJO] No se ejecutó ninguna función directa para esta intención")
    return {"respuesta": "Estoy pensando cómo responderte mejor. Pronto te daré una respuesta."}


