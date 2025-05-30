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
from funciones.explicar_producto import explicar_producto
from routes.chat_flujo_empleados import manejar_flujo_empleados
from routes import chat_functions
from google_sheets_session import cargar_sesion, guardar_sesion
from manejar_peticion_chat import manejar_peticion_chat

logging.basicConfig(level=logging.INFO)
router = APIRouter()

@router.post("")
async def chat_handler(request: Request):
    # Obtener datos de la petición
    client_ip = request.client.host
    body = await request.json()
    mensaje = body.get("mensaje", "").strip()
    mensaje_limpio = mensaje.lower()
    logging.info(f"📥 Petición recibida de {client_ip}: '{mensaje}'")

    # Analizar con manejar_peticion_chat
    datos = manejar_peticion_chat({"mensaje": mensaje, "codsalon": body.get("codsalon")})
    intencion = datos.get("intencion")
    fecha = datos.get("fecha")
    codsalon = datos.get("codsalon")
    codempleado = datos.get("codempleado")
    kpi_detectado = datos.get("kpi")
    logging.info(f"🧠 Intención: {intencion} | Fecha: {fecha} | Salón: {codsalon} | Empleado: {codempleado} | KPI: {kpi_detectado}")

    # Cargar o inicializar sesión usando 'ip'
    sesion = cargar_sesion(client_ip, fecha or "")
    sesion["ip"] = client_ip

    # Flujo interactivo de empleados
    if mensaje_limpio in ["sí", "si", "siguiente", "ok", "vale"] and sesion.get("modo") == "empleados":
        respuesta = manejar_flujo_empleados(sesion)
        guardar_sesion(sesion)
        return {"respuesta": f"Hola, soy Mont Dirección.\n\n{respuesta}"}

    # Actualizar sesión con nuevos datos
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

    # Procesamiento directo según intención
    try:
        # 1) Producto
        if intencion == "explicar_producto":
            nombre_info = datos.get("nombre_producto")
            if not nombre_info:
                return {"respuesta": "No pude identificar el producto. ¿Puedes repetir con más detalle?"}
            prod_name = nombre_info.get("nombre_producto") if isinstance(nombre_info, dict) else nombre_info
            try:
                respuesta_prod = explicar_producto(prod_name)
            except NameError as ne:
                if 'GID_PRODUCTOS' in str(ne):
                    logging.error("GID_PRODUCTOS no definido")
                    raise HTTPException(status_code=500, detail="Configuración de productos incompleta.")
                raise
            if respuesta_prod:
                guardar_sesion(sesion)
                return {"respuesta": f"Hola, soy Mont Dirección.\n\n{respuesta_prod}"}
            return {"respuesta": f"Hola, soy Mont Dirección.\n\nNo encontré información del producto '{prod_name}'. Revisa tus datos en Google Sheets."}

        # 2) Ratios: de más específico a más general
        resultado = None
        if intencion.startswith("explicar_ratio"):
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
            if resultado:
                guardar_sesion(sesion)
                return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error en procesamiento directo: {e}")

    # Fallback: llamada a OpenAI y funciones dinámicas
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres una asistente experta en gestión de salones de belleza."},
                {"role": "user", "content": mensaje}
            ],
            function_call="auto",
            functions=chat_functions.get_definiciones_funciones()
        )
        msg = response.choices[0].message
        if msg.function_call:
            resultado_fnc = chat_functions.resolver(msg.function_call, sesion)
            guardar_sesion(sesion)
            return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado_fnc}"}
        guardar_sesion(sesion)
        return {"respuesta": msg.content or "No se recibió respuesta."}
    except Exception as e:
        logging.error(f"❌ Error en fallback: {e}")
        raise HTTPException(status_code=500, detail="Error interno en el asistente.")
