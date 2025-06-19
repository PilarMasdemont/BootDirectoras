import os
import json
from openai import OpenAI
from src.funciones.selector_dinamico import seleccionar_apartados
from src.funciones.util_json import extraer_fragmentos_desde_rutas


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def consultar_con_chatgpt(pregunta_usuario: str) -> str:
    try:
        # Paso 1: Pedir a ChatGPT qué partes consultar
        rutas = seleccionar_apartados(pregunta_usuario)

        if not rutas:
            return "❗️No encontré ninguna sección relevante para responder a tu pregunta."

        # Paso 2: Extraer contenido de los JSON indicados
        fragmentos = extraer_fragmentos_desde_rutas(rutas)

        if not fragmentos:
            return "❗️No pude obtener contenido útil de los documentos."

        # Paso 3: Construir contexto para el modelo
        contexto = ""
        for clave, contenido in fragmentos.items():
            contexto += f"\n📄 {clave}:\n\"\"\"\n{contenido}\n\"\"\"\n"

        # Paso 4: Armar prompt completo
        prompt = f"""
Eres Mont Dirección, una asistente profesional especializada en productos y procesos de salón de belleza.

La siguiente usuaria tiene esta duda:
"{pregunta_usuario}"

A continuación tienes información útil extraída de los documentos disponibles:
{contexto}

Con esta información, responde de forma clara, útil, y profesional. No inventes. Sé concreta, cálida y segura.
"""

        # Paso 5: Enviar a GPT
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ Error al consultar GPT: {e}"


