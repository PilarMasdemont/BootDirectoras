# funciones/consultar_json_conocimiento.py

from difflib import SequenceMatcher

def similaridad(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def consultar_json_conocimiento(mensaje, base_conocimiento, top_k=3):
    resultados = []
    for entrada in base_conocimiento:
        score = similaridad(mensaje, entrada["contenido"])
        resultados.append((score, entrada))

    resultados.sort(reverse=True, key=lambda x: x[0])
    mejores = resultados[:top_k]

    respuesta = ""
    for _, entrada in mejores:
        if entrada["tipo"] == "lista":
            respuesta += "🔹 Lista:\n" + entrada["contenido"] + "\n\n"
        elif entrada["tipo"] == "pasos":
            respuesta += "🧾 Pasos:\n" + entrada["contenido"] + "\n\n"
        else:
            respuesta += "💬 Info:\n" + entrada["contenido"] + "\n\n"

    return respuesta.strip()
