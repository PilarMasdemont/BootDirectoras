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

import json

router = APIRouter()

@router.post("")
async def chat_handler(request: Request):
    client_ip = request.client.host
    body = await request.json()
    mensaje = body.get("mensaje", "").strip()
    mensaje_limpio = mensaje.lower()

    print(f"📥 Petición recibida de {client_ip}: '{mensaje}'")

    # 📅 Fecha desde el mensaje o body
    fecha = body.get("fecha") or extraer_fecha_desde_texto(mensaje)

    # 📂 Cargar sesión
    sesion = cargar_sesion(client_ip, fecha or "")
    print(f"📂 Sesión cargada: {sesion}")
    sesion["ip_usuario"] = client_ip
    if fecha:
        sesion["fecha"] = fecha

    # ✅ Modo empleados activo
    if mensaje_limpio in ["sí", "si", "siguiente", "ok", "vale"] and sesion.get("modo") == "empleados":
        respuesta = manejar_flujo_empleados(sesion)
        guardar_sesion(sesion)
        return {"respuesta": f"Hola, soy Mont Dirección.\n\n{respuesta}"}

    # 📌 Parámetros contextuales
    kpi_detectado = detectar_kpi(mensaje)
    codsalon = body.get("codsalon") or extraer_codsalon(mensaje) or sesion.get("codsalon")
    codempleado = body.get("codempleado") or extraer_codempleado(mensaje) or sesion.get("codempleado")
    nsemana = body.get("nsemana") or sesion.get("nsemana")
    mes = body.get("mes") or sesion.get("mes")

    if codsalon is not None:
        sesion["codsalon"] = codsalon
    if codempleado is not None:
        sesion["codempleado"] = codempleado
    if kpi_detectado:
        sesion["kpi"] = kpi_detectado
    if nsemana:
        sesion["nsemana"] = nsemana
    if mes:
        sesion["mes"] = mes
    if fecha:
        if fecha != sesion.get("fecha_anterior"):
            sesion["indice_empleado"] = 0
            sesion["fecha_anterior"] = fecha
        sesion["fecha"] = fecha

    # 📊 Procesamiento por función directa
    try:
        if codsalon and fecha and not codempleado and not kpi_detectado:
            resultado = explicar_ratio(codsalon, fecha, mensaje)
        elif codsalon and fecha and codempleado and not kpi_detectado:
            resultado = explicar_ratio_empleado_individual(codsalon, fecha, codempleado)
        elif codsalon and fecha and not codempleado and kpi_detectado:
            resultado = explicar_ratio_diario(codsalon, fecha, kpi_detectado)
        elif codsalon and nsemana and kpi_detectado:
            resultado = explicar_ratio_semanal(codsalon, nsemana, kpi_detectado)
        elif codsalon and mes and kpi_detectado:
            resultado = explicar_ratio_mensual(codsalon, mes, kpi_detectado)
        elif codsalon and fecha and kpi_detectado and codempleado:
            resultado = explicar_ratio_empleados(codsalon, fecha, kpi_detectado, codempleado)
        else:
            resultado = None

        if resultado:
            guardar_sesion(sesion)
            return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}
    except Exception as e:
        print(f"⚠️ Error en funciones directas: {e}")

    # 🤖 Llamada OpenAI si no hubo función directa
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
        print(f"❌ Error en chat_handler: {e}")
        raise HTTPException(status_code=500, detail=str(e))
