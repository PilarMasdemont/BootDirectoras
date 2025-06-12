import json
import openai
from difflib import get_close_matches

# ⚠️ Asegúrate de definir tu clave
openai.api_key = "sk-..."  # mejor usar dotenv o variable de entorno

with open("Archivos_estaticos/process_prueba.json", "r", encoding="utf-8") as f:
    PROCESOS = json.load(f)

ATRIBUTOS_SINONIMOS = {
    "pasos": ["pasos", "cómo se hace", "instrucciones", "orden", "procedimiento"],
    "materiales": ["materiales", "herramientas", "qué se necesita"],
    "duración": ["duración", "tiempo", "cuánto tarda"],
    "responsable": ["quién lo hace", "responsable", "encargado"]
}

def consultar_proceso_chatgpt(nombre_proceso: str, atributo_dudado: str) -> str:
    if not nombre_proceso:
        return "¿Podrías decirme a qué proceso te refieres?"

    # Buscar proceso más cercano
    claves_lower = {k.lower(): k for k in PROCESOS}
    coincidencias = get_close_matches(nombre_proceso.lower(), claves_lower.keys(), n=1, cutoff=0.5)
    if not coincidencias:
        return f"No encontré ningún proceso que se parezca a '{nombre_proceso}'."

    proceso_clave = claves_lower[coincidencias[0]]
    contenido = PROCESOS[proceso_clave].lower()

    # Buscar el atributo
    posibles = ATRIBUTOS_SINONIMOS.get(atributo_dudado.lower(), [atributo_dudado.lower()])
    for palabra in posibles:
        pos = contenido.find(palabra)
        if pos != -1:
            fragmento = contenido[max(0, pos - 100): min(len(contenido), pos + 600)]

            # PROMPT para el modelo
            prompt = f"""
Eres Mont Dirección, una asistente experta en gestión de salones de belleza.
Una peluquera te ha preguntado sobre este proceso: '{proceso_clave}', específicamente sobre '{palabra}'.
A partir del siguiente texto, responde de forma clara, profesional y cercana para ayudarla.

Texto extraído del manual:
{fragmento.strip()}

Respuesta:
"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response["choices"][0]["message"]["content"].strip()

    return f"No encontré información específica sobre '{atributo_dudado}' en el proceso '{proceso_clave}'."
