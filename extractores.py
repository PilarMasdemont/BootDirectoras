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

from datetime import datetime, timedelta
from dateutil import parser
import re


from datetime import datetime, timedelta
from dateutil import parser
import re
import calendar


def extraer_fecha_desde_texto(texto: str, anio_por_defecto=2025) -> str | None:
    """
    Extrae la fecha más relevante desde una cadena de texto.
    - Reconoce: "hoy", "ayer", "hace X días", "el lunes pasado", "el último jueves de mayo", "26 de mayo"
    - Si el año no se menciona, usa `anio_por_defecto`.
    """

    texto = texto.lower()
    hoy = datetime.today()

    # Mapeo español-inglés para el parser
    meses_es_en = {
        "enero": "january", "febrero": "february", "marzo": "march",
        "abril": "april", "mayo": "may", "junio": "june",
        "julio": "july", "agosto": "august", "septiembre": "september",
        "octubre": "october", "noviembre": "november", "diciembre": "december"
    }
    dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

    for es, en in meses_es_en.items():
        texto = texto.replace(es, en)

    # Hoy
    if "hoy" in texto:
        return hoy.strftime("%Y-%m-%d")

    # Ayer
    if "ayer" in texto:
        return (hoy - timedelta(days=1)).strftime("%Y-%m-%d")

    # Hace X días
    match = re.search(r"hace\s+(\d+)\s+d[ií]as?", texto)
    if match:
        dias = int(match.group(1))
        return (hoy - timedelta(days=dias)).strftime("%Y-%m-%d")

    # "el lunes pasado", "el viernes pasado", etc.
    for i, dia in enumerate(dias_semana):
        if f"el {dia} pasado" in texto:
            hoy_idx = hoy.weekday()  # 0=lunes
            delta_dias = (hoy_idx - i + 7) % 7 or 7
            return (hoy - timedelta(days=delta_dias)).strftime("%Y-%m-%d")

    # "el último jueves de mayo"
    match = re.search(r"el último (\w+) de (\w+)", texto)
    if match:
        dia_nombre, mes_nombre = match.groups()
        if dia_nombre in dias_semana and mes_nombre in meses_es_en:
            mes_num = list(meses_es_en.values()).index(mes_nombre) + 1
            dia_idx = dias_semana.index(dia_nombre)
            year = anio_por_defecto

            _, ultimo_dia_mes = calendar.monthrange(year, mes_num)
            for d in range(ultimo_dia_mes, 0, -1):
                fecha = datetime(year, mes_num, d)
                if fecha.weekday() == dia_idx:
                    return fecha.strftime("%Y-%m-%d")

    # Parseo general
    try:
        fecha = parser.parse(texto, fuzzy=True, dayfirst=True)

        # Forzar año por defecto si no se especifica
        if not re.search(r"\b\d{4}\b", texto):
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
