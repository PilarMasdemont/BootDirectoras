from fastapi import APIRouter, Request
import logging
from manejar_peticion_chat import manejar_peticion_chat
from dispatcher import despachar_intencion
from google_sheets_session import cargar_sesion

router = APIRouter()

@router.post("")
async def chat(request: Request):
    body = await request.json()
    mensaje_usuario = body.get("mensaje", "")
    ip = request.client.host

    logging.info(f"📥 Mensaje recibido: {mensaje_usuario}")
    resultado = manejar_peticion_chat(body)

    if resultado.get("intencion") in ["empleado", "general", "kpi"]:
        sesion = cargar_sesion(ip, resultado["fecha"])
        respuesta = despachar_intencion(
            intencion=resultado["intencion"],
            texto_usuario=mensaje_usuario,
            fecha=resultado["fecha"],
            codsalon=resultado["codsalon"],
            codempleado=resultado["codempleado"],
            kpi=resultado["kpi"],
            sesion=sesion
        )
        return {"respuesta": f"Hola, soy Mont Dirección.\n\n{respuesta}"}

    elif resultado.get("intencion") == "documento_estatico":
        return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado['respuesta']}"}

    return {
        "respuesta": "Hola, soy Mont Dirección.\n\nNo encontré información suficiente para responderte."
    }


