from fastapi import APIRouter, Request
import logging

from manejar_peticion_chat import manejar_peticion_chat

router = APIRouter()

@router.post("")
async def chat(request: Request):
    body = await request.json()
    mensaje_usuario = body.get("mensaje", "")
    logging.info(f"📥 Petición recibida: '{mensaje_usuario}'")

    resultado = manejar_peticion_chat(body)

    if "respuesta" in resultado:
        return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado['respuesta']}"}

    return {
        "respuesta": "Hola, soy Mont Dirección.\n\nNo encontré información suficiente para responderte."
    }

