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

def extraer_fecha_desde_texto(texto: str, anio_por_defecto=2025):
    from datetime import datetime, timedelta
    from dateutil import parser
    import re

    texto = texto.lower()

    if "hoy" in texto:
        return datetime.today().strftime("%Y-%m-%d")

    if "ayer" in texto:
        return (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    match = re.search(r"hace\s+(\d+)\s+d[ií]as?", texto)
    if match:
        dias = int(match.group(1))
        return (datetime.today() - timedelta(days=dias)).strftime("%Y-%m-%d")

    # Detectar si el texto incluye explícitamente un año
    hay_anio_explicito = bool(re.search(r"\b\d{4}\b", texto))

    try:
        fecha = parser.parse(texto, fuzzy=True, dayfirst=True)

        if not hay_anio_explicito:
            fecha = fecha.replace(year=anio_por_defecto)

        return fecha.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"❌ Error al interpretar la fecha en el texto '{texto}': {e}")
        return None


def extraer_codsalon(texto: str):
    texto = texto.lower()
    match = re.search(r"sal[oó]n\s*(\d+)", texto)
    if match:
        return match.group(1)
    return None
