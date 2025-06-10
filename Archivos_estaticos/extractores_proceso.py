# Este módulo se encargará de extraer automáticamente el nombre del proceso y 
#la parte específica de la duda (como "duración", "pasos", etc.) desde el texto del usuario.


import json
from difflib import get_close_matches

# Cargar dinámicamente los nombres desde el JSON real
with open("Archivos_estaticos/process_prueba.json", "r", encoding="utf-8") as f:
    LISTA_PROCESOS = list(json.load(f).keys())

DUDAS_COMUNES = [
    "duración", "pasos", "cómo se hace", "quién lo hace", "responsable",
    "materiales", "instrucciones", "qué se necesita", "orden", "funciona", "flujo", "procedimiento"
]

def extraer_nombre_proceso(texto: str) -> str:
    texto = texto.lower()
    coincidencias = get_close_matches(texto, LISTA_PROCESOS, n=1, cutoff=0.4)
    return coincidencias[0] if coincidencias else None

def extraer_duda_proceso(texto: str) -> str:
    texto = texto.lower()
    for duda in DUDAS_COMUNES:
        if duda in texto:
            return duda
    return None

