# Este módulo se encargará de extraer automáticamente el nombre del proceso y 
#la parte específica de la duda (como "duración", "pasos", etc.) desde el texto del usuario.


from difflib import get_close_matches
import json

with open("Archivos_estaticos/process_prueba.json", "r", encoding="utf-8") as f:
    LISTA_PROCESOS = list(json.load(f).keys())

def extraer_nombre_proceso(texto: str) -> str:
    texto = texto.lower().strip()
    lista_lower = {k.lower(): k for k in LISTA_PROCESOS}
    
    # Coincidencia exacta
    if texto in lista_lower:
        return lista_lower[texto]
    
    # Coincidencia aproximada
    coincidencias = get_close_matches(texto, lista_lower.keys(), n=1, cutoff=0.5)
    if coincidencias:
        return lista_lower[coincidencias[0]]
    
    return None


