import os
import json
from openai import OpenAI
from funciones.util_json import extraer_fragmentos_desde_rutas

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def seleccionar_y_responder_con_documentos(pregunta_usuario: str) -> str:
    try:
        # Cargar índice con estructura: documento, ruta, descripcion
        indice_path = "Archivos_estaticos/indice_doc.json"
        with open(indice_path, encoding="utf-8") as f:
            indice = json.load(f)

        # Crear lista legible de títulos para mostrar a ChatGPT
        lista_docs = ""
        for item in indice:
            ruta = item.get("ruta", [""])[0]
            descripcion = item.get("descripcion", "")
            lista_docs += f"- {ruta}: {descripcion}\n"

        # Preguntar a ChatGPT qué claves de ruta usar
        prompt_seleccion = f"""
El usuario ha hecho esta pregunta:
\"\"\"{pregunta_usuario}\"\"\"

A continuación hay una lista de documentos disponibles con sus descripciones.

{lista_docs}

Según esta lista, ¿qué documentos son los más útiles para responder la pregunta del usuario? 
Devuélveme solo los nombres exactos de ruta (por ejemplo: inventario_manual, mechas_tipos_precios), separados por coma si son varios. 
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

        claves_seleccionadas = [clave.strip() for clave in seleccion.split(",")]
        rutas_relevantes = []

        for clave in claves_seleccionadas:
            for item in indice:
                if item.get("ruta", [""])[0] == clave:
                    rutas_relevantes.append({
                        "documento": item["documento"],
                        "ruta": item["ruta"]
                    })

        if not rutas_relevantes:
            return None

        fragmentos = extraer_fragmentos_desde_rutas(rutas_relevantes)

        contexto = ""
        for clave, contenido in fragmentos.items():
            contexto += f"\n📄 {clave}:\n\"\"\"\n{contenido}\n\"\"\"\n"

        if not contexto:
            return None

        # Construir el prompt final con contexto real
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



