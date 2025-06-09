from fastapi import APIRouter, Request
import logging
import json
from openai import OpenAI
from routes.chat_functions import resolver, get_definiciones_funciones
from memory import user_context

router = APIRouter()
client = OpenAI()  # Nuevo cliente requerido en openai>=1.0.0

@router.post("")
async def chat(request: Request):
    body = await request.json()
    mensaje = body.get("mensaje", "")
    codsalon = body.get("codsalon")
    ip_usuario = request.client.host

    logging.info(f"📥 Petición recibida: '{mensaje}' (salón: {codsalon}, IP: {ip_usuario})")

    funciones_llm = get_definiciones_funciones()
    logging.info(f"🔧 Funciones LLM disponibles: {[f['name'] for f in funciones_llm]}")

    respuesta_llm = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                "content": "Eres Mont Dirección. Si detectas intención de explicar un ratio, llama a la función correspondiente. Si detectas que te piden definir un KPI, usa la función definir_kpi."
            },
            {
                "role": "user",
                "content": mensaje
            }
        ],
        functions=funciones_llm,
        function_call="auto"
    )

    respuesta = respuesta_llm.choices[0].message
    logging.info(f"🤖 Respuesta LLM recibida. Function call: {respuesta.function_call}")

    if respuesta.function_call:
        nombre_funcion = respuesta.function_call.name
        argumentos = respuesta.function_call.arguments
        logging.info(f"📞 Llamada a función: {nombre_funcion} con argumentos {argumentos}")

        fecha_llamada = json.loads(argumentos).get("fecha", "")
        logging.info(f"🕓 Fecha usada en sesión: {fecha_llamada}")

        sesion = user_context[(ip_usuario, fecha_llamada)]
        sesion["codsalon"] = codsalon

        try:
            resultado = resolver(respuesta.function_call, sesion)
            logging.info(f"✅ Resultado generado: {resultado}")
            return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}
        except Exception as e:
            logging.exception("[ERROR] Al ejecutar función:")
            return {"respuesta": f"Ocurrió un error al procesar tu petición: {str(e)}"}

    logging.info("📭 Respuesta directa del modelo sin función.")
    return {"respuesta": respuesta.content or "No he entendido tu mensaje."}

