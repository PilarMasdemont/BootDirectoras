# chat_router.py
from fastapi import APIRouter, Request, HTTPException
from config import setup_environment, openai_client
from extractores import detectar_kpi, extraer_fecha_desde_texto, extraer_codempleado, extraer_codsalon
from funciones.explicar_ratio import explicar_ratio
from routes.chat_flujo_empleados import manejar_flujo_empleados
from routes import chat_functions
import os
import json

# 🌐 Detectar si se debe usar Google Drive o Google Sheets
USE_GOOGLE_DRIVE = os.getenv("USE_GOOGLE_DRIVE", "false").lower() == "true"
if USE_GOOGLE_DRIVE:
    from session_io_drive import cargar_estado_sesion as cargar_sesion
    from session_io_drive import guardar_estado_sesion as guardar_sesion
else:
    from google_sheets_session import cargar_sesion, guardar_sesion

router = APIRouter()

@router.post("")
async def chat_handler(request: Request):
    print("💡 Chat handler activado")
    client_ip = request.client.host
    body = await request.json()
    mensaje = body.get("mensaje", "").strip()
    mensaje_limpio = mensaje.lower()

    print(f"📥 Petición recibida de {client_ip}: '{mensaje}'")

    fecha = body.get("fecha") or extraer_fecha_desde_texto(mensaje)
    sesion = cargar_sesion(client_ip, fecha or "")
    print(f"📂 Sesión cargada: {sesion}")
    sesion["ip_usuario"] = client_ip
    if fecha:
        sesion["fecha"] = fecha

    if mensaje_limpio in ["sí", "si", "siguiente", "ok", "vale"] and sesion.get("modo") == "empleados":
        respuesta = manejar_flujo_empleados(sesion)
        print(f"🛠️ Manejando flujo empleados, respuesta: {respuesta}")
        guardar_sesion(sesion, client_ip, sesion["fecha"])
        return {"respuesta": f"Hola, soy Mont Dirección.\n\n{respuesta}"}

    kpi_detectado = detectar_kpi(mensaje)
    codsalon = body.get("codsalon") or extraer_codsalon(mensaje) or sesion.get("codsalon")
    nsemana = body.get("nsemana") or sesion.get("nsemana")
    mes = body.get("mes") or sesion.get("mes")
    codempleado = body.get("codempleado") or extraer_codempleado(mensaje) or sesion.get("codempleado")

    for key, val in [
        ("codsalon", codsalon), ("nsemana", nsemana),
        ("mes", mes), ("codempleado", codempleado), ("kpi", kpi_detectado)
    ]:
        if val is not None:
            sesion[key] = val

    if fecha:
        if fecha != sesion.get("fecha_anterior"):
            sesion["indice_empleado"] = 0
            sesion["fecha_anterior"] = fecha
        sesion["fecha"] = fecha

    if codsalon and fecha:
        try:
            respuesta_directa = explicar_ratio(codsalon, fecha, mensaje)
            guardar_sesion(sesion, client_ip, fecha)
            return {"respuesta": f"Hola, soy Mont Dirección.\n\n{respuesta_directa}"}
        except Exception as e:
            print(f"⚠️ Error en respuesta directa: {e}")

    system_prompt = """... (prompt personalizado del sistema) ..."""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mensaje}
            ],
            function_call="auto",
            functions=chat_functions.get_definiciones_funciones()
        )
        msg = response.choices[0].message
        if msg.function_call:
            resultado = chat_functions.resolver(msg.function_call, sesion)
            guardar_sesion(sesion, client_ip, sesion["fecha"])
            return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}

        guardar_sesion(sesion, client_ip, sesion["fecha"])
        return {"respuesta": msg.content or "No se recibió contenido del asistente."}
    except Exception as e:
        print(f"❌ Error en chat_handler: {e}")
        raise HTTPException(status_code=500, detail=str(e))
