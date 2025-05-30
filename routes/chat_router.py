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
from funciones.explicar_producto import explicar_producto

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

    # Analizar petición
    datos = manejar_peticion_chat({"mensaje": mensaje, "codsalon": body.get("codsalon")})
    intencion = datos["intencion"]
    fecha = datos["fecha"]
    codsalon = datos["codsalon"]
    codempleado = datos["codempleado"]
    kpi_detectado = datos["kpi"]

    logging.info(f"🧠 Intención: {intencion}")
    logging.info(f"📅 Fecha extraída: {fecha}")
    logging.info(f"🏢 Salón: {codsalon}")
    logging.info(f"👤 Empleado: {codempleado}")
    logging.info(f"📊 KPI: {kpi_detectado}")

    # Cargar sesión
    sesion = cargar_sesion(client_ip, fecha or "")
    sesion["ip_usuario"] = client_ip

    # Modo empleados interactivo
    if mensaje_limpio in ["sí", "si", "siguiente", "ok", "vale"] and sesion.get("modo") == "empleados":
        respuesta = manejar_flujo_empleados(sesion)
        guardar_sesion(sesion)
        return {"respuesta": f"Hola, soy Mont Dirección.\n\n{respuesta}"}

    # Actualizar sesión
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

    # Procesamiento directo según intención y datos disponibles
    resultado = None
    try:
        if intencion == "explicar_producto":
            nombre_producto = datos.get("nombre_producto")
            if nombre_producto:
                resultado = explicar_producto(nombre_producto)
            else:
                return {"respuesta": "No pude identificar el producto del que me hablas. ¿Puedes repetirlo con más detalle?"}
        elif intencion.startswith("explicar_ratio"):
            # Flujo KPI: casos desde más específico a más general
            if codsalon and fecha and codempleado and kpi_detectado:
                resultado = explicar_ratio_empleados(codsalon, fecha, kpi_detectado, codempleado)
            elif codsalon and fecha and codempleado:
                resultado = explicar_ratio_empleado_individual(codsalon, fecha, codempleado)
            elif codsalon and fecha and kpi_detectado:
                resultado = explicar_ratio_diario(codsalon, fecha, kpi_detectado)
            elif codsalon and sesion.get("nsemana") and kpi_detectado:
                resultado = explicar_ratio_semanal(codsalon, sesion["nsemana"], kpi_detectado)
            elif codsalon and sesion.get("mes") and kpi_detectado:
                resultado = explicar_ratio_mensual(codsalon, sesion["mes"], kpi_detectado)
            elif codsalon and fecha:
                resultado = explicar_ratio(codsalon, fecha, mensaje)
        # Si se obtuvo resultado, guardamos y devolvemos
        if resultado:
            guardar_sesion(sesion)
            return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}
    except Exception as e:
        logging.error(f"⚠️ Error en procesamiento directo: {e}")

    # Llamada a OpenAI como fallback
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


