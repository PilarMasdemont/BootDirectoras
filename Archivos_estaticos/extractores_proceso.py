# Este módulo se encargará de extraer automáticamente el nombre del proceso y 
#la parte específica de la duda (como "duración", "pasos", etc.) desde el texto del usuario.

import json

# Cargar diccionario de alias desde el archivo alias_procesos.json
with open("Archivos_estaticos/alias_procesos.json", "r", encoding="utf-8") as f:
    ALIASES_PROCESOS = json.load(f)

def extraer_nombre_proceso(texto: str) -> str:
    texto = texto.lower()
    for alias, real in ALIASES_PROCESOS.items():
        if alias in texto:
            return real
    return None

def extraer_duda_proceso(texto: str) -> str:
    texto = texto.lower()
    posibles = [
        "duración", "cuánto tarda", "pasos", "cómo se hace", "instrucciones",
        "quién lo hace", "responsable", "materiales", "herramientas", "orden", "funciona", "flujo"
    ]
    for p in posibles:
        if p in texto:
            return p
    return None








