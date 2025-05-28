from fastapi import APIRouter, Request
from funciones.intencion import clasificar_intencion
from funciones.extraer_codempleado import extraer_codempleado
from funciones.explicar_ratio import responder
from funciones.utils import limpiar_fecha
from datetime import datetime
import os

USE_GOOGLE_DRIVE = os.getenv("USE_GOOGLE_DRIVE", "false").lower() == "true"

if USE_GOOGLE_DRIVE:
    from session_io_drive import cargar_estado_sesion as cargar_sesion
    from session_io_drive import guardar_estado_sesion as guardar_sesion
else:
    from google_sheets_session import cargar_estado_sesion as cargar_sesion
    from google_sheets_session import guardar_estado_sesion as guardar_sesion

router = APIRouter()

@router.post("")
async def chat_handler(request: Request):
    try:
        data = await request.json()
        mensaje = data.get("mensaje", "")
        client_ip = request.client.host
        print(f"📥 Petición recibida de {client_ip}: '{mensaje}'")

        # Extraer fecha
        fecha = limpiar_fecha(mensaje)
        if not fecha:
            fecha = datetime.now().strftime("%Y-%m-%d")

        # Cargar sesión (Drive o Sheets)
        sesion = cargar_sesion(client_ip, fecha or "")
        if sesion is None:
            print("📁 No se encontró sesión en Drive, creando nueva sesión.")
            sesion = {
                "ip_usuario": client_ip,
                "fecha": fecha,
                "codsalon": None,
                "modo": "",
                "indice_empleado": 0,
                "ultima_interaccion": "",
                "codempleado": None,
                "nsemana": "",
                "mes": "",
                "kpi": "",
                "fecha_anterior": ""
            }
        else:
            print(f"📂 Sesión cargada correctamente: {sesion}")

        sesion["ip_usuario"] = client_ip
        sesion["fecha"] = fecha

        # Clasificar intención
        intencion = clasificar_intencion(mensaje)
        print(f"🤖 Intención detectada: {intencion}")

        # Extraer codempleado si aplica
        codempleado = extraer_codempleado(mensaje)
        if codempleado:
            sesion["codempleado"] = codempleado

        # Llamar al asistente
        respuesta, sesion_actualizada = responder(mensaje, sesion)

        # Guardar nueva sesión
        if USE_GOOGLE_DRIVE:
            guardar_sesion(sesion_actualizada, client_ip, fecha)
        else:
            guardar_sesion(sesion_actualizada)

        return {"respuesta": respuesta}

    except Exception as e:
        print(f"❌ Error en chat_handler: {e}")
        return {"respuesta": "⚠️ Ha ocurrido un error al procesar tu mensaje. Inténtalo de nuevo."}
