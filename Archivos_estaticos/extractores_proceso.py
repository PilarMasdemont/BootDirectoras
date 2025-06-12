# Este módulo se encargará de extraer automáticamente el nombre del proceso y 
#la parte específica de la duda (como "duración", "pasos", etc.) desde el texto del usuario.


import json
from difflib import get_close_matches

# Cargar lista de procesos
with open("Archivos_estaticos/process_prueba.json", "r", encoding="utf-8") as f:
    PROCESOS = json.load(f)
    CLAVES_PROCESOS = list(PROCESOS.keys())

def extraer_nombre_proceso(texto: str) -> str:
    texto = texto.lower()
    claves_lower = {k.lower(): k for k in CLAVES_PROCESOS}

    # Revisión exacta o parcial
    tokens = texto.split()
    mejores = []

    for clave_lower in claves_lower:
        match_score = sum(1 for token in tokens if token in clave_lower)
        mejores.append((match_score, clave_lower))

    mejores = sorted(mejores, reverse=True)
    if mejores and mejores[0][0] > 0:
        return claves_lower[mejores[0][1]]

    # Fuzzy matching de respaldo
    coincidencias = get_close_matches(texto.lower(), claves_lower.keys(), n=1, cutoff=0.5)
    if coincidencias:
        return claves_lower[coincidencias[0]]

    return None

def extraer_duda_proceso(texto: str) -> str:
    texto = texto.lower()
    patrones = ["duración", "cuánto tarda", "quién lo hace", "responsable", "cómo se hace", "pasos", "materiales", "orden"]
    for patron in patrones:
        if patron in texto:
            return patron
    return None






