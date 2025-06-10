import json
from difflib import get_close_matches

# Carga del archivo JSON una única vez (podrías moverlo a una función si necesitas recargar dinámicamente)
with open("Archivos_estaticos/process_prueba.json", "r", encoding="utf-8") as f:
    PROCESOS = json.load(f)

def consultar_proceso(nombre_proceso: str, atributo_dudado: str) -> str:
    if not nombre_proceso:
        return "No estoy segura a qué proceso te refieres. ¿Podrías darme un poco más de contexto?"
    if not nombre_proceso and not atributo_dudado:
        return "¿Podrías especificar sobre qué proceso o tema quieres saber más (por ejemplo: inventario, agenda, caja)?"



    # Buscar el proceso más similar
    coincidencias = get_close_matches(nombre_proceso.lower(), PROCESOS.keys(), n=1, cutoff=0.7)
    if not coincidencias:
        return f"No encontré ningún proceso que se parezca a '{nombre_proceso}'."

    proceso_clave = coincidencias[0]
    contenido = PROCESOS[proceso_clave].lower()

    if not atributo_dudado:
        return f"Encontré el proceso '{proceso_clave}', pero necesito que me digas qué parte te interesa (por ejemplo, duración, pasos, materiales...)."

    # Buscar el atributo en el contenido
    pos = contenido.find(atributo_dudado)
    if pos == -1:
        return f"No encontré información específica sobre '{atributo_dudado}' en el proceso '{proceso_clave}'."

    # Extraer ventana de texto alrededor del atributo
    inicio = max(0, pos - 100)
    fin = min(len(contenido), pos + 500)
    fragmento = contenido[inicio:fin]

    return f"🔍 Información sobre **{atributo_dudado}** en **{proceso_clave}**:\n\n{fragmento.strip()}"
