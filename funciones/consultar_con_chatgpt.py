import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def seleccionar_y_responder_con_documentos(pregunta_usuario: str) -> str:
    try:
        indice_path = "Archivos_estaticos/indice_doc.json"
        with open(indice_path, encoding="utf-8") as f:
            indice = json.load(f)

        lista_docs = ""
        for item in indice:
            nombre = item.get("nombre")
            descripcion = item.get("descripcion")
            lista_docs += f"- {nombre}: {descripcion}\n"

        prompt_seleccion = f"""
El usuario ha hecho esta pregunta:
\"\"\"{pregunta_usuario}\"\"\"

A continuación hay una lista de documentos disponibles con sus descripciones.

{lista_docs}

Según esta lista, ¿qué documentos son los más útiles para responder la pregunta del usuario? 
Devuélveme solo los nombres exactos de archivo, separados por coma si son varios (por ejemplo: inventario_manual.json, productos.json). 
No expliques nada más.
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt_seleccion}],
            temperature=0
        )
        seleccion = response.choices[0].message.content.strip()

        if not seleccion:
            return None

        nombres_docs = [nombre.strip() for nombre in seleccion.split(",")]

        contexto = ""
        for nombre in nombres_docs:
            ruta_doc = os.path.join("Archivos_estaticos", nombre)
            if os.path.exists(ruta_doc):
                with open(ruta_doc, encoding="utf-8") as f:
                    contenido = f.read()
                contexto += f"\n📄 {nombre}:\n\"\"\"\n{contenido}\n\"\"\"\n"

        if not contexto:
            return None

        prompt_respuesta = f"""
Eres Mont Dirección, una asistente profesional especializada en productos y procesos de salón de belleza.

La usuaria ha preguntado lo siguiente:
\"\"\"{pregunta_usuario}\"\"\"

Aquí tienes información útil extraída de los documentos relevantes:
{contexto}

Con base en esta información, responde de forma clara, útil y profesional. Sé cálida, concreta y no inventes datos.
"""

        respuesta_final = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt_respuesta}],
            temperature=0.5
        )

        return respuesta_final.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ Error al procesar los documentos: {str(e)}"


