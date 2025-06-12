# Este módulo se encargará de extraer automáticamente el nombre del proceso y 
#la parte específica de la duda (como "duración", "pasos", etc.) desde el texto del usuario.

import json
from difflib import get_close_matches

# Cargar dinámicamente los nombres desde el JSON real
with open("Archivos_estaticos/process_prueba.json", "r", encoding="utf-8") as f:
    PROCESOS = json.load(f)
    LISTA_PROCESOS = list(PROCESOS.keys())

DUDAS_COMUNES = [
    "duración", "pasos", "cómo se hace", "quién lo hace", "responsable",
    "materiales", "instrucciones", "qué se necesita", "orden", "funciona", "flujo", "procedimiento"
]

def extraer_nombre_proceso(texto: str) -> str:
    texto = texto.lower()
    # Intentamos encontrar coincidencia aproximada con cualquiera de las palabras clave en el JSON
    for clave in LISTA_PROCESOS:
        if any(palabra in texto for palabra in clave.lower().split()):
            return clave

    # Si no hay coincidencia clara, usar fuzzy matching
    lista_lower = {k.lower(): k for k in LISTA_PROCESOS}
    coincidencias = get_close_matches(texto.lower(), lista_lower.keys(), n=1, cutoff=0.4)
    if coincidencias:
        return lista_lower[coincidencias[0]]

    return None

def extraer_duda_proceso(texto: str) -> str:
    texto = texto.lower()
    for duda in DUDAS_COMUNES:
        if duda in texto:
            return duda
    return None



