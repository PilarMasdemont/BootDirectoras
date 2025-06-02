# handlers/chat_functions.py
import json
from funciones.explicar_ratio_diario import explicar_ratio_diario
from funciones.explicar_ratio_semanal import explicar_ratio_semanal
from funciones.explicar_ratio_mensual import explicar_ratio_mensual
from funciones.explicar_ratio_empleados import explicar_ratio_empleados
from funciones.explicar_ratio_empleado_individual import explicar_ratio_empleado_individual


def get_definiciones_funciones():
    return [
        {
            "name": "explicar_ratio_diario",
            "description": "Explica ratios diarios.",
            "parameters": {
                "type": "object",
                "properties": {
                    "codsalon": {"type": "string"},
                    "fecha": {"type": "string"}
                },
                "required": ["codsalon", "fecha"]
            }
        },
        {
            "name": "explicar_ratio_semanal",
            "description": "Explica ratios semanales.",
            "parameters": {
                "type": "object",
                "properties": {
                    "codsalon": {"type": "string"},
                    "nsemana": {"type": "integer"}
                },
                "required": ["codsalon", "nsemana"]
            }
        },
        {
            "name": "explicar_ratio_mensual",
            "description": "Explica ratios mensuales.",
            "parameters": {
                "type": "object",
                "properties": {
                    "codsalon": {"type": "string"},
                    "mes": {"type": "string"},
                    "codempleado": {"type": "string"}
                },
                "required": ["codsalon", "mes", "codempleado"]
            }
        },
        {
            "name": "explicar_ratio_empleados",
            "description": "Explica ratios de cada trabajador de forma progresiva.",
            "parameters": {
                "type": "object",
                "properties": {
                    "codsalon": {"type": "string"},
                    "fecha": {"type": "string"}
                },
                "required": ["codsalon", "fecha"]
            }
        },
        {
            "name": "explicar_ratio_empleado_individual",
            "description": "Explica ratio de un empleado individual.",
            "parameters": {
                "type": "object",
                "properties": {
                    "codsalon": {"type": "string"},
                    "fecha": {"type": "string"},
                    "codempleado": {"type": "string"}
                },
                "required": ["codsalon", "fecha", "codempleado"]
            }
        }
    ]


def resolver(function_call, sesion: dict) -> str:
    nombre_funcion = function_call.name
    argumentos = json.loads(function_call.arguments)

    if nombre_funcion == "explicar_ratio_diario":
        return explicar_ratio_diario(**argumentos)
    elif nombre_funcion == "explicar_ratio_semanal":
        return explicar_ratio_semanal(**argumentos)
    elif nombre_funcion == "explicar_ratio_mensual":
        return explicar_ratio_mensual(**argumentos)
    elif nombre_funcion == "explicar_ratio_empleado_individual":
        return explicar_ratio_empleado_individual(**argumentos)
    elif nombre_funcion == "explicar_ratio_empleados":
        indice = sesion.get("indice_empleado", 0)
        resultado = explicar_ratio_empleados(
            codsalon=argumentos["codsalon"],
            fecha=argumentos["fecha"],
            indice=indice
        )
        sesion["indice_empleado"] = indice + 1
        sesion["modo"] = "empleados"
        return resultado
    else:
        raise ValueError("Función no reconocida")

from config import openai_client

def generar_respuesta(prompt: str) -> str:
    """Genera una respuesta usando el modelo GPT basado en un prompt de usuario."""
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Responde con claridad y profesionalismo para asesorar a una directora de salón de peluquería. Utiliza el archivo de productos si aplica."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

