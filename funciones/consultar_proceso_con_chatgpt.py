import os
import json
from openai import OpenAI
from difflib import get_close_matches
from unidecode import unidecode

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("Archivos_estaticos/process_prueba.json", "r", encoding="utf-8") as f:
    PROCESOS = json.load(f)

def normalizar(texto):
    return unidecode(texto.lower().strip())

def encontrar_proceso(nombre_usuario: str) -> str:
    nombre_norm = normalizar(nombre_usuario)

    claves_lower = {normalizar(k): k for k in PROCESOS}
    coincidencias = get_close_matches(nombre_norm, claves_lower.keys(), n=1, cutoff=0.6)

    if coincidencias:
        return claves_lower[coincidencias[0]]

    # Si no hay coincidencia fuerte, buscar por inclusión
    for key_norm, original_key in claves_lower.items():
        if nombre_norm in key_norm or key_norm in nombre_norm:
            return original_key

    return None

def consultar_proceso_chatgpt(nombre_proceso: str, pregunta_usuario: str) -> str:
    proceso_clave = encontrar_proceso(nombre_proceso)

    if not proceso_clave:
        return f"❗️No encontré ningún proceso que se parezca a '{nombre_proceso}'."

    contenido = PROCESOS[proceso_clave]

    prompt = f"""
Eres Mont Dirección, una asistente experta en gestión de salones de belleza.

A continuación tienes el contenido completo del proceso llamado **{proceso_clave}**:
\"\"\"
{contenido}
\"\"\"

Con esta información, responde de forma clara, profesional y práctica a esta pregunta que hizo una usuaria:

**{pregunta_usuario}**

No inventes nada que no aparezca en el texto.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error al consultar GPT: {e}"





