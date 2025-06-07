from collections import defaultdict

# Estructura base para cada sesión en memoria
estructura_base = lambda: {
    "modo": None,
    "codsalon": None,
    "indice_empleado": 0,
    "ultima_interaccion": None,
    "codempleado": None,
    "nsemana": None,
    "mes": None,
    "kpi": None,
    "fecha_anterior": None,
    "hoja_consultada": None,     # ← Nuevo campo
    "funcion_utilizada": None,   # ← Nuevo campo
    "intencion": None            # ← Nuevo campo
}

user_context = defaultdict(estructura_base)
