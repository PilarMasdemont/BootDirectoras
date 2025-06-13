import os
import json
from openai import OpenAI
from difflib import get_close_matches
from unidecode import unidecode  # ✅ para normalizar texto

# Cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Cargar los procesos desde el JSON
with open("Archivos_estaticos/process_prueba.json", "r", encoding="utf-8") as f:
    PROCESOS = json.load(f)

def normalizar(texto: str) -> str:
    return unidecode(texto.strip().lower())

def consultar_proceso_chatgpt(nombre_proceso: str, atributo_dudado: str) -> str:
    if not nombre_proceso:
        return "❗️No estoy segura a qué proceso te refieres. ¿Podrías especificarlo un poco más?"

    # Crear diccionario normalizado de claves
    claves_normalizadas = {normalizar(k): k for k in PROCESOS}
    entrada_normalizada = normalizar(nombre_proceso)

    # Buscar coincidencia flexible
    coincidencias = get_close_matches(entrada_normalizada, claves_normalizadas.keys(), n=1, cutoff=0.3)

    if coincidencias:
        proceso_clave = claves_normalizadas[coincidencias[0]]
    else:
        # Buscar en el contenido
        proceso_clave = None
        for k, v in PROCESOS.items():
            if entrada_normalizada in normalizar(v):
                proceso_clave = k
                break

        if not proceso_clave:
            return f"❗️No encontré ningún proceso relacionado con '{nombre_proceso}'."

    contenido = PROCESOS[proceso_clave]

    # Prompt para el modelo
    prompt = f"""
Eres Mont Dirección, una asistente especializada en gestión de salones de belleza. 
Una usuaria te ha preguntado sobre el proceso **{proceso_clave}**, específicamente sobre: **{atributo_dudado}**.

A continuación tienes el contenido del procedimiento:
\"\"\"
{contenido}
\"\"\"

Con esta información, responde de forma clara, profesional y práctica. No inventes información que no aparezca.

Respuesta:
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error al consultar GPT: {e}"



