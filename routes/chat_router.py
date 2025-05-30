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
    intencion = datos.get("intencion")
    fecha = datos.get("fecha")
    codsalon = datos.get("codsalon")
    codempleado = datos.get("codempleado")
    kpi_detectado = datos.get("kpi")

    logging.info(f"🧠 Intención: {intencion}")
    logging.info(f"📅 Fecha extraída: {fecha}")
    logging.info(f"🏢 Salón: {codsalon}")
    logging.info(f"👤 Empleado: {codempleado}")
    logging.info(f"📊 KPI: {kpi_detectado}")

    # Cargar sesión (usa clave 'ip')
    sesion = cargar_sesion(client_ip, fecha or "")
    sesion["ip"] = client_ip

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
    try:
        resultado = None
        if intencion == "explicar_producto":
            nombre_info = datos.get("nombre_producto")
            logging.debug(f"📋 datos incoming nombre_producto: {nombre_info}")
            if nombre_info:
                prod_name = nombre_info.get("nombre_producto") if isinstance(nombre_info, dict) else nombre_info
                logging.debug(f"📋 llamando explicar_producto con prod_name: '{prod_name}'")
                try:
                    resultado = explicar_producto(prod_name)
                    logging.debug(f"📋 resultado explicar_producto raw: {resultado!r}")
                except NameError as ne:
                    if 'GID_PRODUCTOS' in str(ne):
                        logging.error("❌ Constante GID_PRODUCTOS no definida en explicar_producto.")
                        return {"respuesta": "Error interno: configuración de productos incompleta (GID_PRODUCTOS no definido). Por favor, revisa la configuración del conector a Google Sheets."}
                    else:
                        logging.error(f"❌ Excepción en explicar_producto: {ne}")
                except Exception as ex:
                    logging.error(f"❌ Excepción en explicar_producto: {ex}")
                if resultado:
                    guardar_sesion(sesion)
                    return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}
                logging.info(f"📋 No se encontró info completa para '{prod_name}', columnas disponibles: {resultado.keys() if isinstance(resultado, dict) else 'None'}")
                return {"respuesta": f"Hola, soy Mont Dirección.\n\nNo encontré información completa sobre el producto '{prod_name}'. Comprueba que las columnas en Google Sheets estén bien definidas."}
            else:
                return {"respuesta": "No pude identificar el producto del que me hablas. ¿Puedes repetirlo con más detalle?"}
        elif intencion.startswith("explicar_ratio"):
            # Flujo KPI...
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
    except Exception as e:
        logging.error(f"⚠️ Error en procesamiento directo: {e}")

    # Fallback a OpenAI
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Eres una asistente especializada en explicar indicadores de gestión de salones de belleza."},
                      {"role": "user", "content": mensaje}],
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
