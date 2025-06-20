import json
from openai import OpenAI

client = OpenAI()

def seleccionar_apartados(pregunta_usuario, ruta_indice="Archivos_estaticos/indice_doc.json"):
    # Cargar el índice de documentos plano
    with open(ruta_indice, "r", encoding="utf-8") as f:
        documentos = json.load(f)

    # Armar el contenido que se le da al modelo
    lista_docs = ""
    for doc in documentos:
        ruta_str = " > ".join(doc["ruta"])
        descripcion = doc.get("descripcion", "")
        lista_docs += f"- ({doc['documento']}) {ruta_str}: {descripcion}\n"

    # Crear el prompt
    prompt = f"""
Tienes acceso a los siguientes documentos JSON con sus apartados clave:

{lista_docs}

El usuario ha preguntado lo siguiente:
\"\"\"{pregunta_usuario}\"\"\"

Tu tarea es responder con una lista JSON de las rutas necesarias para responder. Por ejemplo:
[
  {{ "documento": "productos_diccionario.json", "ruta": ["mascarilla_reparadora"] }},
  {{ "documento": "process_prueba.json", "ruta": ["inventario_manual"] }}
]
No expliques nada más. Solo responde con la lista JSON.
"""

    # Llamar al modelo
    response = client.chat.completions.create(
        model="gpt-4",
        temperature=0,
        messages=[
            {"role": "system", "content": "Eres un asistente que ayuda a seleccionar apartados de documentos JSON."},
            {"role": "user", "content": prompt}
        ]
    )

    # Parsear respuesta del modelo
    respuesta_modelo = response.choices[0].message.content
    try:
        return json.loads(respuesta_modelo)
    except:
        print("⚠️ El modelo no devolvió un JSON válido.")
        return []

