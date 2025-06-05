import logging
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException
from config import setup_environment, openai_client
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

    # 🔍 DEBUG - Verificación de extracción
    logging.info(f"🧠 Intención: {intencion}")
    logging.info(f"📅 Fecha extraída: {fecha}")
    logging.info(f"🏢 Salón: {codsalon}")
    logging.info(f"👤 Empleado: {codempleado}")
    logging.info(f"📊 KPI: {kpi_detectado}")

    # 📂 Cargar sesión
    sesion = cargar_sesion(client_ip, fecha or "")
    logging.info(f"📂 Sesión cargada: {sesion}")
    sesion["ip_usuario"] = client_ip

    # ✅ Modo empleados activo
    if mensaje_limpio in ["sí", "si", "siguiente", "ok", "vale"] and sesion.get("modo") == "empleados":
        from routes.chat_flujo_empleados import manejar_flujo_empleados
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

    # 🎯 Procesamiento por intención a través de resolver()
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres una asistente especializada en explicar indicadores de gestión de salones de belleza."},
                {"role": "user", "content": mensaje}
            ],
            function_call="auto",
            functions=chat_functions.get_definiciones_funciones()
        )

        msg = response.choices[0].message
        if msg.function_call:
            resultado = chat_functions.resolver(msg.function_call, sesion)
            guardar_sesion(sesion)
            return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}

        guardar_sesion(sesion)
        return {"respuesta": msg.content or "No se recibió contenido del asistente."}

    except Exception as e:
        logging.error(f"❌ Error en chat_handler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


