# extractores.py
import re
from datetime import datetime
from dateutil import parser

def detectar_kpi(texto: str):
    texto = texto.lower()
    if "productividad" in texto:
        return "productividad"
    elif "clientes nuevos" in texto or "nuevos clientes" in texto:
        return "clientes_nuevos"
    elif "servicio" in texto:
        return "servicios"
    return None

def extraer_codempleado(texto: str):
    texto = texto.lower()
    match = re.search(r"emplead[oa]\s*(\d+)", texto)
    if match:
        return match.group(1)
    return None

def extraer_fecha_desde_texto(texto):
    texto = texto.lower()
    if "hoy" in texto:
        return datetime.today().strftime("%Y-%m-%d")
    if "ayer" in texto:
        return (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        fecha = parser.parse(texto, fuzzy=True)
        return fecha.strftime("%Y-%m-%d")
    except Exception:
        return None

def extraer_codsalon(texto: str):
    texto = texto.lower()
    match = re.search(r"sal[oó]n\s*(\d+)", texto)
    if match:
        return match.group(1)
    return None
