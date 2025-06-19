import os
import json
from openai import OpenAI
from difflib import get_close_matches

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("Archivos_estaticos/productos_diccionario.json", "r", encoding="utf-8") as f:
    PRODUCTOS = json.load(f)

def consultar_producto_chatgpt(nombre_producto: str, atributo_dudado: str) -> str:
    if not nombre_producto:
        return "❗️No estoy segura a qué producto te refieres. ¿Podrías especificarlo un poco más?"

    claves_lower = {k.lower(): k for k in PRODUCTOS}
    coincidencias = get_close_matches(nombre_producto.lower(), claves_lower.keys(), n=1, cutoff=0.5)
    if not coincidencias:
        return f"❗️No encontré ningún producto que se parezca a '{nombre_producto}'."

    producto_clave = claves_lower[coincidencias[0]]
    contenido = PRODUCTOS[producto_clave]

    prompt = f"""
Eres Mont Dirección, una asistente especializada en gestión de salones de belleza. 
Una usuaria te ha preguntado sobre el producto **{producto_clave}**, específicamente sobre: **{atributo_dudado}**.

A continuación tienes la información del producto:
"""
{contenido}
"""

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




