import re

KPI_LIST = [
    "ratiogeneral",
    "facturacionsiva",
    "ratiodesviaciontiempoteorico",
    "ratioticketsinferior20",
    "ratiotiempoindirecto",
    "ticketsivamedio",
    "horasfichadas"
]

def detectar_kpi(texto):
    texto = texto.lower()
    for kpi in KPI_LIST:
        if kpi in texto:
            return kpi
    return None

def extraer_fecha_desde_texto(texto):
    meses = {
        "enero": "01", "febrero": "02", "marzo": "03", "abril": "04", "mayo": "05",
        "junio": "06", "julio": "07", "agosto": "08", "septiembre": "09",
        "octubre": "10", "noviembre": "11", "diciembre": "12"
    }

    texto = texto.lower()
    match = re.search(r"(\d{1,2})\s+de\s+([a-zñ]+)(?:\s+de\s+(\d{4}))?", texto)
    if match:
        dia = match.group(1).zfill(2)
        mes = meses.get(match.group(2))
        anio = match.group(3) or "2025"
        if mes:
            return f"{anio}-{mes}-{dia}"
    return None
    import re

def extraer_codempleado(texto: str):
    texto = texto.lower()
    match = re.search(r"empleado\s*(\d+)", texto)
    if match:
        return match.group(1)
    return None
