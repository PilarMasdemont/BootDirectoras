import os
import json
import openai
import logging
from difflib import get_close_matches

# Setup logging
logging.basicConfig(level=logging.INFO)

# API Key desde variable de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")

# Carga el contenido del JSON
with open("Archivos_estaticos/process_prueba.json", "r", encoding="utf-8") as f:
    PROCESOS = json.load(f)

def consultar_proceso_chatgpt(nombre_proceso: str, atributo_dudado: str) -> str:
    if not nombre_proceso:
        return "❗️No estoy segura a qué proceso te refieres. ¿Podrías especificarlo un poco más?"

    if not atributo_dudado:
        atributo_dudado = "información general"

    # Normalización de claves
    claves_lower = {k.lower(): k for k in PROCESOS}
    coincidencias = get_close_matches(nombre_proceso.lower(), claves_lower.keys(), n=1, cutoff=0.5)
    if not coincidencias:
        return f"❗️No encontré ningún proceso que se parezca a '{nombre_proceso}'."

    proceso_clave = claves_lower[coincidencias[0]]
    contenido = PROCESOS[proceso_clave]

    # Construcción del prompt
    prompt = f"""
Eres Mont Dirección, una asistente especializada en gestión de salones de belleza. 
Una usuaria del equipo te ha preguntado sobre el proceso **{proceso_clave}**, específicamente sobre: **{atributo_dudado}**.

A continuación tienes el contenido completo del procedimiento:
\"\"\"
{contenido}
\"\"\"

Usando esta información, responde de forma clara, profesional y práctica solo con lo que aparece en el texto. 
No inventes datos que no estén presentes. Sé directa y cercana.

Respuesta:
""".strip()

    logging.info("🧠 Prompt enviado a ChatGPT:\n" + prompt)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        # logging.info("📩 Respuesta completa GPT:\n" + str(response))  # opcional
        return response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        logging.error(f"❌ Error al consultar ChatGPT: {e}")
        return f"❌ Error al consultar GPT: {e}"




