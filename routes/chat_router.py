
import logging
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException
from config import setup_environment, openai_client
from extractores import detectar_kpi, extraer_fecha_desde_texto, extraer_codempleado, extraer_codsalon
from funciones.explicar_ratio import explicar_ratio
from funciones.explicar_ratio_empleados import explicar_ratio_empleados
from funciones.explicar_ratio_empleado_individual import explicar_ratio_empleado_individual
from funciones.explicar_ratio_diario import explicar_ratio_diario
from funciones.explicar_ratio_mensual import explicar_ratio_mensual
from funciones.explicar_ratio_semanal import explicar_ratio_semanal
from routes.chat_flujo_empleados import manejar_flujo_empleados
from routes import chat_functions
from google_sheets_session import cargar_sesion, guardar_sesion
from manejar_peticion_chat import manejar_peticion_chat

import json

logging.basicConfig(level=logging.INFO)

router = APIRouter()

@router.post("")
async def chat_handler(request: Request):
    client_ip = request.client.host
    body = await request.json()
    mensaje = body.get("mensaje", "").strip()
    mensaje_limpio = mensaje.lower()

    logging.info(f"📥 Petición recibida de {client_ip}: '{mensaje}'")

    # 🧠 Analizar petición
    datos = manejar_peticion_chat({"mensaje": mensaje, "codsalon": body.get("codsalon")})
    intencion = datos["intencion"]
    fecha = datos["fecha"]
    codsalon = datos["codsalon"]
    codempleado = datos["codempleado"]
    kpi_detectado = datos["kpi"]
    tiene_fecha = datos["tiene_fecha"]

    logging.info(f"🧠 Intención: {intencion}")
    logging.info(f"📅 Fecha extraída: {fecha}")
    logging.info(f"🏢 Salón: {codsalon}")
    logging.info(f"👤 Empleado: {codempleado}")
    logging.info(f"📊 KPI: {kpi_detectado}")

    # 📂 Cargar sesión
    sesion = cargar_sesion(client_ip, fecha or "")
    sesion["ip_usuario"] = client_ip
    logging.info(f"📂 Sesión cargada: {sesion}")

    # ✅ Modo empleados activo
    if mensaje_limpio in ["sí", "si", "siguiente", "ok", "vale"] and sesion.get("modo") == "empleados":
        respuesta = manejar_flujo_empleados(sesion)
        guardar_sesion(sesion)
        return {"respuesta": f"Hola, soy Mont Dirección.\n\n{respuesta}"}

    # 📌 Actualizar sesión
    if codsalon is not None:
        sesion["codsalon"] = codsalon
    if codempleado is not None:
        sesion["codempleado"] = codempleado
    if kpi_detectado:
        sesion["kpi"] = kpi_detectado
    if fecha:
        if fecha != sesion.get("fecha_anterior"):
            sesion["indice_empleado"] = 0
            sesion["fecha_anterior"] = fecha
        sesion["fecha"] = fecha

    # 🔀 Bifurcación según tipo de intención
    try:
        if intencion == "explicar_producto":
            prompt = f"Este es el mensaje del usuario: '{mensaje}'. Proporciónale información útil sobre el producto basándote en el archivo markdown de productos."
            respuesta = chat_functions.generar_respuesta(prompt)
        elif tiene_fecha:
            if codsalon and fecha and not codempleado and not kpi_detectado:
                respuesta = explicar_ratio(codsalon, fecha, mensaje)
            elif codsalon and fecha and codempleado and not kpi_detectado:
                respuesta = explicar_ratio_empleado_individual(codsalon, codempleado, fecha, mensaje)
            elif codsalon and fecha and codempleado and kpi_detectado:
                respuesta = explicar_ratio_empleados(codsalon, fecha, codempleado, kpi_detectado)
            elif codsalon and fecha and kpi_detectado and "día" in mensaje_limpio:
                respuesta = explicar_ratio_diario(codsalon, fecha, kpi_detectado)
            elif codsalon and fecha and kpi_detectado and "semana" in mensaje_limpio:
                respuesta = explicar_ratio_semanal(codsalon, fecha, kpi_detectado)
            elif codsalon and fecha and kpi_detectado and "mes" in mensaje_limpio:
                respuesta = explicar_ratio_mensual(codsalon, fecha, kpi_detectado)
            else:
                prompt = f"El usuario ha dicho: '{mensaje}'. Usa el modelo para generar una respuesta útil con base en la fecha proporcionada."
                respuesta = chat_functions.generar_respuesta(prompt)
        else:
            prompt = f"El usuario ha dicho: '{mensaje}'. Responde de forma clara y útil, sin usar datos históricos."
            respuesta = chat_functions.generar_respuesta(prompt)
    except Exception as e:
        logging.error(f"❌ Error al procesar mensaje: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

    guardar_sesion(sesion)
    return {"respuesta": f"Hola, soy Mont Dirección.\n\n{respuesta}"}




