from fastapi import APIRouter, Request
import logging

from funciones.intencion_total import clasificar_intencion_completa
from funciones.consultar_proceso_con_chatgpt import consultar_proceso_chatgpt
from funciones.extractores_proceso import (
    extraer_nombre_proceso,
    extraer_duda_proceso,
    extraer_nombre_proceso_desde_alias,
    cargar_jsons_por_alias
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

@router.post("")
async def chat(request: Request):
    body = await request.json()
    mensaje_usuario = body.get("mensaje", "")
    codsalon = body.get("codsalon")
    intencion_info = clasificar_intencion_completa(mensaje_usuario)
    intencion = intencion_info["intencion"]

    # Detectar proceso por alias o texto
    nombre_proceso = intencion_info.get("proceso") or extraer_nombre_proceso_desde_alias(mensaje_usuario)
    if not nombre_proceso:
        nombre_proceso = extraer_nombre_proceso(mensaje_usuario)

    # Validar fecha
    fecha_detectada = extraer_fecha_desde_texto(mensaje_usuario)
    fecha = fecha_detectada if fecha_detectada != "FECHA_NO_VALIDA" else None

    if fecha:
        actualizar_contexto(codsalon, "fecha", fecha)

    # Si hay proceso detectado, consultar con chatgpt usando los archivos relevantes
    if nombre_proceso:
        documentos = cargar_jsons_por_alias(nombre_proceso)
        respuesta = consultar_proceso_chatgpt(nombre_proceso, mensaje_usuario, documentos)
        return {"respuesta": f"Hola, soy Mont Dirección.\n\n{respuesta}"}

    # Si no hay proceso, usar dispatcher
    resultado = despachar_intencion(
        intencion=intencion,
        texto_usuario=mensaje_usuario,
        fecha=fecha,
        codsalon=codsalon,
        codempleado=extraer_codempleado(mensaje_usuario),
        kpi=detectar_kpi(mensaje_usuario),
        sesion=obtener_contexto(codsalon),
    )

    return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado or 'Estoy pensando cómo responderte mejor.'}"}








