import json
from difflib import get_close_matches

# Carga única del JSON de procesos
with open("Archivos_estaticos/process_prueba.json", "r", encoding="utf-8") as f:
    PROCESOS = json.load(f)

def consultar_proceso(nombre_proceso: str, atributo_dudado: str) -> str:
    if not nombre_proceso and not atributo_dudado:
        return "¿Podrías especificar sobre qué proceso o tema quieres saber más (por ejemplo: inventario, agenda, caja)?"

    if not nombre_proceso:
        return "No estoy segura a qué proceso te refieres. ¿Podrías darme un poco más de contexto?"

    # Buscar proceso con coincidencia flexible
    nombre_proceso = nombre_proceso.lower()
    claves_lower = {k.lower(): k for k in PROCESOS.keys()}
    
    # Match exacto
    if nombre_proceso in claves_lower:
        proceso_clave = claves_lower[nombre_proceso]
    else:
        # Match aproximado con fuzzy matching
        coincidencias = get_close_matches(nombre_proceso, claves_lower.keys(), n=1, cutoff=0.5)
        if not coincidencias:
            return f"No encontré ningún proceso que se parezca a '{nombre_proceso}'."
        proceso_clave = claves_lower[coincidencias[0]]

    contenido = PROCESOS[proceso_clave].lower()

    if not atributo_dudado:
        return f"Encontré el proceso **{proceso_clave}**, pero necesito que me digas qué parte te interesa (por ejemplo: duración, pasos, materiales...)."

    # Buscar el atributo dentro del contenido
    pos = contenido.find(atributo_dudado.lower())
    if pos == -1:
        return f"No encontré información específica sobre **{atributo_dudado}** en el proceso **{proceso_clave}**."

    inicio = max(0, pos - 100)
    fin = min(len(contenido), pos + 500)
    fragmento = contenido[inicio:fin]

    return f"🔍 Información sobre **{atributo_dudado}** en **{proceso_clave}**:\n\n{fragmento.strip()}"

