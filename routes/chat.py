from fastapi import APIRouter, Request, HTTPException
from config import openai_client
from funciones.explicar_ratio_diario import explicar_ratio_diario
from funciones.explicar_ratio_semanal import explicar_ratio_semanal
from funciones.explicar_ratio_mensual import explicar_ratio_mensual
from funciones.explicar_ratio import explicar_ratio
from funciones.explicar_ratio_empleados import explicar_ratio_empleados
from funciones.explicar_ratio_empleado_individual import explicar_ratio_empleado_individual
from extractores import detectar_kpi, extraer_fecha_desde_texto, extraer_codempleado
from memory import user_context
import json
import re

router = APIRouter()

def extraer_codsalon(texto):
    texto = texto.lower()
    match = re.search(r"sal[oó]n\s*(\d+)", texto)
    if match:
        return match.group(1)
    return None

@router.post("/chat")
async def chat_handler(request: Request):
    client_ip = request.client.host
    body = await request.json()
    mensaje = body.get("mensaje", "")

mensaje_limpio = mensaje.strip().lower()

if mensaje_limpio in ["sí", "si", "siguiente", "ok", "vale"] and user_context[client_ip].get("modo") == "empleados":
    codsalon = user_context[client_ip].get("codsalon")
    fecha = user_context[client_ip].get("fecha")
    indice = user_context[client_ip].get("indice_empleado", 0)

    if codsalon and fecha:
        resultado = explicar_ratio_empleados(codsalon, fecha, indice)
        user_context[client_ip]["indice_empleado"] = indice + 1
        return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}

    mensaje_limpio = mensaje.strip().lower()

    kpi_detectado = detectar_kpi(mensaje)
    codsalon = body.get("codsalon") or extraer_codsalon(mensaje) or user_context[client_ip].get("codsalon")
    fecha = body.get("fecha") or extraer_fecha_desde_texto(mensaje) or user_context[client_ip].get("fecha")
    nsemana = body.get("nsemana") or user_context[client_ip].get("nsemana")
    mes = body.get("mes") or user_context[client_ip].get("mes")
    codempleado = body.get("codempleado") or extraer_codempleado(mensaje) or user_context[client_ip].get("codempleado")

    if codsalon: user_context[client_ip]["codsalon"] = codsalon
    if fecha: user_context[client_ip]["fecha"] = fecha
    if nsemana: user_context[client_ip]["nsemana"] = nsemana
    if mes: user_context[client_ip]["mes"] = mes
    if codempleado: user_context[client_ip]["codempleado"] = codempleado
    if kpi_detectado: user_context[client_ip]["kpi"] = kpi_detectado

    # ✅ Reseteo de índice si cambia la fecha
    if fecha and fecha != user_context[client_ip].get("fecha_anterior"):
        user_context[client_ip]["indice_empleado"] = 0
        user_context[client_ip]["fecha_anterior"] = fecha

    # ✅ Continuación de flujo si el usuario responde "sí", "siguiente", etc.
    if mensaje_limpio in ["sí", "si", "siguiente", "ok"] and user_context[client_ip].get("modo") == "empleados":
        codsalon = user_context[client_ip].get("codsalon")
        fecha = user_context[client_ip].get("fecha")
        indice = user_context[client_ip].get("indice_empleado", 0)

        if codsalon and fecha:
            resultado = explicar_ratio_empleados(codsalon, fecha, indice)
            user_context[client_ip]["indice_empleado"] = indice + 1
            return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}

    system_prompt = """... (tu prompt personalizado, sin cambios) ..."""

    try:
        if codsalon and fecha:
            try:
                respuesta_directa = explicar_ratio(codsalon, fecha, mensaje)
                return {"respuesta": f"Hola, soy Mont Dirección.\n\n{respuesta_directa}"}
            except Exception:
                pass

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mensaje}
            ],
            function_call="auto",
            functions=[
                {
                    "name": "explicar_ratio_diario",
                    "description": "...",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "codsalon": {"type": "string"},
                            "fecha": {"type": "string"}
                        },
                        "required": ["codsalon", "fecha"]
                    },
                },
                {
                    "name": "explicar_ratio_semanal",
                    "description": "...",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "codsalon": {"type": "string"},
                            "nsemana": {"type": "integer"}
                        },
                        "required": ["codsalon", "nsemana"]
                    },
                },
                {
                    "name": "explicar_ratio_mensual",
                    "description": "...",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "codsalon": {"type": "string"},
                            "mes": {"type": "string"},
                            "codempleado": {"type": "string"}
                        },
                        "required": ["codsalon", "mes", "codempleado"]
                    },
                },
                {
                    "name": "explicar_ratio_empleados",
                    "description": "Explica los ratios de cada trabajador de forma progresiva.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "codsalon": {"type": "string"},
                            "fecha": {"type": "string"}
                        },
                        "required": ["codsalon", "fecha"]
                    },
                },
                {
                    "name": "explicar_ratio_empleado_individual",
                    "description": "...",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "codsalon": {"type": "string"},
                            "fecha": {"type": "string"},
                            "codempleado": {"type": "string"}
                        },
                        "required": ["codsalon", "fecha", "codempleado"]
                    },
                },
            ]
        )

        msg = response.choices[0].message
        if msg.function_call:
            nombre_funcion = msg.function_call.name
            argumentos = json.loads(msg.function_call.arguments)

            if nombre_funcion == "explicar_ratio_diario":
                resultado = explicar_ratio_diario(**argumentos)
            elif nombre_funcion == "explicar_ratio_semanal":
                resultado = explicar_ratio_semanal(**argumentos)
            elif nombre_funcion == "explicar_ratio_mensual":
                resultado = explicar_ratio_mensual(**argumentos)
            elif nombre_funcion == "explicar_ratio_empleado_individual":
                resultado = explicar_ratio_empleado_individual(**argumentos)
            elif nombre_funcion == "explicar_ratio_empleados":
                indice = user_context[client_ip].get("indice_empleado", 0)
                resultado = explicar_ratio_empleados(
                    codsalon=argumentos["codsalon"],
                    fecha=argumentos["fecha"],
                    indice=indice
                )
                user_context[client_ip]["indice_empleado"] = indice + 1
                user_context[client_ip]["modo"] = "empleados"  # ✅ activa el modo para siguientes
            else:
                raise HTTPException(status_code=400, detail="Función no reconocida")

            return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}

        return {"respuesta": msg.content or "No se recibió contenido del asistente."}

    except Exception as e:
        return {"error": str(e)}
