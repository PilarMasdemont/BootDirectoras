# Este módulo se encargará de extraer automáticamente el nombre del proceso y 
#la parte específica de la duda (como "duración", "pasos", etc.) desde el texto del usuario.


import json
from difflib import get_close_matches

# Cargar procesos
with open("Archivos_estaticos/process_prueba.json", "r", encoding="utf-8") as f:
    PROCESOS = json.load(f)
    CLAVES_PROCESOS = list(PROCESOS.keys())

# Alias manualmente definidos
ALIASES_PROCESOS = {
    "cerrar caja": "CERRAR CAJA MANUAL",
    "cierre de caja": "CERRAR CAJA MANUAL",
    "cierre caja manual": "CERRAR CAJA MANUAL",
    "caja": "CERRAR CAJA MANUAL",
    "proceso caja": "CERRAR CAJA MANUAL",
    "cierre de caja manual": "CERRAR CAJA MANUAL"
}

def extraer_nombre_proceso(texto: str) -> str:
    texto = texto.lower().strip()

    for alias, real in ALIASES_PROCESOS.items():
        if alias in texto:
            return real

    # Coincidencia fuzzy como respaldo
    claves_lower = {k.lower(): k for k in CLAVES_PROCESOS}
    coincidencias = get_close_matches(texto, claves_lower.keys(), n=1, cutoff=0.5)
    if coincidencias:
        return claves_lower[coincidencias[0]]

    return None

def extraer_duda_proceso(texto: str) -> str:
    texto = texto.lower()
    posibles = [
        "duración", "pasos", "cómo se hace", "quién lo hace",
        "responsable", "materiales", "orden", "instrucciones"
    ]
    for p in posibles:
        if p in texto:
            return p
    return None







