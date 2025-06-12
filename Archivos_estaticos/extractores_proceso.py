# Este módulo se encargará de extraer automáticamente el nombre del proceso y 
#la parte específica de la duda (como "duración", "pasos", etc.) desde el texto del usuario.
import json
from difflib import get_close_matches

# Cargar lista de procesos desde el archivo JSON
with open("Archivos_estaticos/process_prueba.json", "r", encoding="utf-8") as f:
    PROCESOS = json.load(f)
    CLAVES_PROCESOS = list(PROCESOS.keys())

DUDAS_COMUNES = [
    "duración", "pasos", "cómo se hace", "quién lo hace", "responsable",
    "materiales", "instrucciones", "qué se necesita", "orden", "funciona", "flujo", "procedimiento"
]

def extraer_nombre_proceso(texto: str) -> str:
    texto = texto.lower()

    # Normalizar claves
    claves_lower = {k.lower(): k for k in CLAVES_PROCESOS}

    # 1. Coincidencia exacta
    if texto in claves_lower:
        return claves_lower[texto]

    # 2. Coincidencia por palabra clave contenida
    for clave in claves_lower:
        if all(pal in clave for pal in texto.split()):
            return claves_lower[clave]
        if any(pal in clave for pal in texto.split()):
            return claves_lower[clave]

    # 3. Fuzzy matching
    coincidencias = get_close_matches(texto, claves_lower.keys(), n=1, cutoff=0.4)
    if coincidencias:
        return claves_lower[coincidencias[0]]

    return None

def extraer_duda_proceso(texto: str) -> str:
    texto = texto.lower()
    for duda in DUDAS_COMUNES:
        if duda in texto:
            return duda
    return None




