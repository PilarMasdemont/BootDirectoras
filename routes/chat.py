from fastapi import APIRouter, Request, HTTPException
from config import openai_client
from funciones.explicar_ratio_diario import explicar_ratio_diario
from funciones.explicar_ratio_semanal import explicar_ratio_semanal
from funciones.explicar_ratio_mensual import explicar_ratio_mensual
from extractores import detectar_kpi, extraer_fecha_desde_texto
from memory import user_context
import json

router = APIRouter()

@router.post("/chat")
async def chat_handler(request: Request):
    client_ip = request.client.host
    body = await request.json()
    mensaje = body.get("mensaje", "")
    kpi_detectado = detectar_kpi(mensaje)
    codsalon = body.get("codsalon") or user_context[client_ip].get("codsalon")
    fecha = body.get("fecha") or extraer_fecha_desde_texto(mensaje) or user_context[client_ip].get("fecha")
    nsemana = body.get("nsemana") or user_context[client_ip].get("nsemana")
    mes = body.get("mes") or user_context[client_ip].get("mes")
    codempleado = body.get("codempleado") or user_context[client_ip].get("codempleado")

    if codsalon: user_context[client_ip]["codsalon"] = codsalon
    if fecha: user_context[client_ip]["fecha"] = fecha
    if nsemana: user_context[client_ip]["nsemana"] = nsemana
    if mes: user_context[client_ip]["mes"] = mes
    if codempleado: user_context[client_ip]["codempleado"] = codempleado
    if kpi_detectado: user_context[client_ip]["kpi"] = kpi_detectado

    system_prompt = """
Eres Mont Dirección, una asistente especializada en el análisis de salones de belleza...

Eres Mont Dirección, una asistente especializada en el análisis de salones de belleza.

Tu objetivo es ayudar a las directoras a interpretar los resultados operativos, basándote exclusivamente en los siguientes KPIs:

- facturacionsiva: mide ingresos sin IVA.
- ratiodesviaciontiempoteorico: mide la diferencia entre el tiempo planificado y el tiempo realmente trabajado.
- ratiogeneral: relaciona la facturación con el coste del personal.
- ratioticketsinferior20: porcentaje de tickets con importe inferior a 20 €.
- ratiotiempoindirecto: porcentaje de tiempo no productivo (no atendiendo clientes).
- ticketsivamedio: importe medio por ticket (solo informativo).
- horasfichadas: tiempo total fichado (solo informativo).

Nunca menciones KPIs que no estén en esta lista.

📅 Analizas datos del **año 2025**.

Puedes explicar KPIs en tres niveles:
- 📌 Diario (requiere: codsalon y fecha).
- 📆 Semanal (requiere: codsalon y número de semana).
- 📊 Mensual (requiere: codsalon, mes y código del empleado).

📌 Si falta un dato, solicita amablemente la información antes de responder.

⚙️ Invoca las funciones disponibles automáticamente según el mensaje:
- explicar_ratio_diario
- explicar_ratio_semanal
- explicar_ratio_mensual

📎 Usa solo los datos proporcionados por el usuario o disponibles en los parámetros. No inventes información.

Tus respuestas deben ser claras, profesionales.
""".strip()

    try:
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
                    "description": "Explica el valor del Ratio General en un día concreto.",
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
                    "description": "Explica el valor del Ratio General semanal de un salón.",
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
                    "description": "Explica el valor del Ratio General mensual de un salón.",
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
            else:
                raise HTTPException(status_code=400, detail="Función no reconocida")

            return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}

        return {"respuesta": msg.content or "No se recibió contenido del asistente."}

    except Exception as e:
        return {"error": str(e)}