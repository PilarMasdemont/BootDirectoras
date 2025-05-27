# chat_router.py
from fastapi import APIRouter, Request, HTTPException
from config import openai_client
from extractores import detectar_kpi, extraer_fecha_desde_texto, extraer_codempleado
from funciones.explicar_ratio import explicar_ratio
from routes.chat_flujo_empleados import manejar_flujo_empleados
from routes.chat_functions import ejecutar_funcion_llamada
from utils import extraer_codsalon
from google_sheets_session import cargar_sesion, guardar_sesion
import json

router = APIRouter()

@router.post("/chat")
async def chat_handler(request: Request):
    client_ip = request.client.host
    body = await request.json()
    mensaje = body.get("mensaje", "").strip()
    mensaje_limpio = mensaje.lower()

    # Cargar sesión persistente
    fecha = body.get("fecha") or extraer_fecha_desde_texto(mensaje)
    sesion = cargar_sesion(client_ip, fecha or "")
    sesion["ip_usuario"] = client_ip
    if fecha:
        sesion["fecha"] = fecha

    # Paso 1: flujo de empleados
    if mensaje_limpio in ["sí", "si", "siguiente", "ok", "vale"] and sesion.get("modo") == "empleados":
        respuesta = manejar_flujo_empleados(sesion)
        guardar_sesion(sesion)
        return {"respuesta": f"Hola, soy Mont Dirección.\n\n{respuesta}"}

    # Paso 2: extraer parámetros
    kpi_detectado = detectar_kpi(mensaje)
    codsalon = body.get("codsalon") or extraer_codsalon(mensaje) or sesion.get("codsalon")
    fecha = fecha or sesion.get("fecha")
    nsemana = body.get("nsemana") or sesion.get("nsemana")
    mes = body.get("mes") or sesion.get("mes")
    codempleado = body.get("codempleado") or extraer_codempleado(mensaje) or sesion.get("codempleado")

    # Actualizar sesión
    if codsalon: sesion["codsalon"] = codsalon
    if fecha:
        if fecha != sesion.get("fecha_anterior"):
            sesion["indice_empleado"] = 0
            sesion["fecha_anterior"] = fecha
        sesion["fecha"] = fecha
    if nsemana: sesion["nsemana"] = nsemana
    if mes: sesion["mes"] = mes
    if codempleado: sesion["codempleado"] = codempleado
    if kpi_detectado: sesion["kpi"] = kpi_detectado

    # Paso 3: intentar respuesta directa
    if codsalon and fecha:
        try:
            respuesta_directa = explicar_ratio(codsalon, fecha, mensaje)
            guardar_sesion(sesion)
            return {"respuesta": f"Hola, soy Mont Dirección.\n\n{respuesta_directa}"}
        except Exception:
            pass

    # Paso 4: invocar modelo OpenAI
    system_prompt = """... (tu prompt personalizado, sin cambios) ..."""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mensaje}
            ],
            function_call="auto",
            functions=ejecutar_funcion_llamada.get_definiciones_funciones()
        )

        msg = response.choices[0].message
        if msg.function_call:
            resultado = ejecutar_funcion_llamada.resolver(msg.function_call, sesion)
            guardar_sesion(sesion)
            return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}

        return {"respuesta": msg.content or "No se recibió contenido del asistente."}

    except Exception as e:
        return {"error": str(e)}


