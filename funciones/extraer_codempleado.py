import re

def extraer_codempleado(texto: str):
    texto = texto.lower()
    match = re.search(r"empleado\s*(\d+)", texto)
    if match:
        return match.group(1)
    return None
