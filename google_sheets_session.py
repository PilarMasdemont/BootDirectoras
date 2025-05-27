from funciones import (
    explicar_ratio, explicar_ratio_mensual, explicar_ratio_semanal,
    explicar_ratio_diario, explicar_ratio_empleados,
    explicar_ratio_empleado_individual
)

def get_definiciones_funciones():
    return [
        {
            "name": "explicar_ratio_general",
            "description": "Explica el ratio general de un salón en una fecha dada.",
            "parameters": {
                "type": "object",
                "properties": {
                    "codsalon": {"type": "string"},
                    "fecha": {"type": "string", "format": "date"}
                },
                "required": ["codsalon", "fecha"]
            }
        },
        {
            "name": "explicar_ratio_mensual",
            "description": "Explica el ratio de un salón durante un mes específico.",
            "parameters": {
                "type": "object",
                "properties": {
                    "codsalon": {"type": "string"},
                    "mes": {"type": "string"}
                },
                "required": ["codsalon", "mes"]
            }
        },
        {
            "name": "explicar_ratio_semanal",
            "description": "Explica el ratio de un salón durante una semana específica.",
            "parameters": {
                "type": "object",
                "properties": {
                    "codsalon": {"type": "string"},
                    "nsemana": {"type": "string"}
                },
                "required": ["codsalon", "nsemana"]
            }
        },
        {
            "name": "explicar_ratio_diario",
            "description": "Explica el ratio de un salón en un día específico.",
            "parameters": {
                "type": "object",
                "properties": {
                    "codsalon": {"type": "string"},
                    "fecha": {"type": "string", "format": "date"}
                },
                "required": ["codsalon", "fecha"]
            }
        },
        {
            "name": "explicar_ratio_empleados",
            "description": "Explica el ratio de todos los empleados de un salón en una fecha específica.",
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
            "description": "Explica el ratio de un empleado individual de un salón en una fecha específica.",
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

def resolver(function_call, sesion):
    nombre_funcion = function_call.name
    argumentos = function_call.arguments.dict() if hasattr(function_call.arguments, 'dict') else {}

    print("🧠 Nombre de función a resolver:", nombre_funcion)
    print("📦 Argumentos recibidos:", argumentos)

    if nombre_funcion == "explicar_ratio_general":
        return explicar_ratio(**argumentos)
    elif nombre_funcion == "explicar_ratio_mensual":
        return explicar_ratio_mensual(**argumentos)
    elif nombre_funcion == "explicar_ratio_semanal":
        return explicar_ratio_semanal(**argumentos)
    elif nombre_funcion == "explicar_ratio_diario":
        return explicar_ratio_diario(**argumentos)
    elif nombre_funcion == "explicar_ratio_empleados":
        return explicar_ratio_empleados(**argumentos, sesion=sesion)
    elif nombre_funcion == "explicar_ratio_empleado_individual":
        return explicar_ratio_empleado_individual(**argumentos, sesion=sesion)
    else:
        return f"No se reconoce la función: {nombre_funcion}"
