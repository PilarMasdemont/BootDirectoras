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


from datetime import datetime, timedelta
from dateutil import parser
import re
import calendar


def extraer_fecha_desde_texto(texto: str, anio_por_defecto=2025):
    texto = texto.lower()

    meses_es_en = {
        "enero": "january", "febrero": "february", "marzo": "march",
        "abril": "april", "mayo": "may", "junio": "june",
        "julio": "july", "agosto": "august", "septiembre": "september",
        "octubre": "october", "noviembre": "november", "diciembre": "december"
    }

    dias_semana = {
        "lunes": 0, "martes": 1, "miércoles": 2, "miercoles": 2,
        "jueves": 3, "viernes": 4, "sábado": 5, "sabado": 5, "domingo": 6
    }

    # Convertir números escritos a dígitos
    numeros_texto = {
        "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
        "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10
    }
    for palabra, numero in numeros_texto.items():
        texto = re.sub(rf"\\b{palabra}\\b", str(numero), texto)

    for es, en in meses_es_en.items():
        texto = texto.replace(es, en)

    hoy = datetime.today()

    if "hoy" in texto:
        return hoy.strftime("%Y-%m-%d")

    if "ayer" in texto:
        return (hoy - timedelta(days=1)).strftime("%Y-%m-%d")

    match = re.search(r"hace\\s+(\\d+)\\s+d[ií]as?", texto)
    if match:
        dias = int(match.group(1))
        return (hoy - timedelta(days=dias)).strftime("%Y-%m-%d")

    match = re.search(r"el\\s+(lunes|martes|miércoles|miercoles|jueves|viernes|sábado|sabado|domingo)\\s+pasado", texto)
    if match:
        dia_nombre = match.group(1)
        dia_target = dias_semana[dia_nombre]
        dias_diferencia = (hoy.weekday() - dia_target + 7) % 7 or 7
        fecha_objetivo = hoy - timedelta(days=dias_diferencia)
        return fecha_objetivo.strftime("%Y-%m-%d")

    match = re.search(r"el\\s+último\\s+(lunes|martes|miércoles|miercoles|jueves|viernes|sábado|sabado|domingo)\\s+de\\s+(\\w+)", texto)
    if match:
        dia_nombre = match.group(1)
        mes_nombre = match.group(2)

        try:
            mes_en = meses_es_en[mes_nombre]
            mes = list(meses_es_en.keys()).index(mes_nombre) + 1
            anio = anio_por_defecto

            _, ultimo_dia = calendar.monthrange(anio, mes)

            for dia in range(ultimo_dia, 0, -1):
                fecha = datetime(anio, mes, dia)
                if fecha.weekday() == dias_semana[dia_nombre]:
                    return fecha.strftime("%Y-%m-%d")
        except:
            pass

    try:
        fecha = parser.parse(texto, fuzzy=True, dayfirst=True)

        if not re.search(r"\\b\\d{4}\\b", texto):
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
