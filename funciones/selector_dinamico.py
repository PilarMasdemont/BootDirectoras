import json
from openai import OpenAI

client = OpenAI()

def seleccionar_apartados(pregunta_usuario, ruta_indice="Archivos_estaticos/indice_docs.json"):
    # Cargar el índice de documentos y descripciones
    with open(ruta_indice, "r", encoding="utf-8") as f:
        documentos = json.load(f)

    # Armar el contenido que se le da al modelo
    lista_docs = ""
    for doc in documentos:
        lista_docs += f"\n📄 {doc['documento']}:\n"
        for clave in doc["claves"]:
            ruta_str = " > ".join(clave["ruta"])
            lista_docs += f"  - {ruta_str}: {clave['descripcion']}\n"

    # Crear el prompt
    prompt = f"""
Tienes acceso a los siguientes documentos JSON con sus subapartados:

{lista_docs}

El usuario ha preguntado lo siguiente:
"{pregunta_usuario}"

Tu tarea es responder con una lista JSON de las rutas necesarias para responder. Por ejemplo:
[
  {{ "documento": "productos_diccionario.json", "ruta": ["Silhouette Laca Fuerte"] }},
  {{ "documento": "process_prueba.json", "ruta": ["Tratamientos en frio conocimiento para las chicas"] }}
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

    # Parsear respuesta
    respuesta_modelo = response.choices[0].message.content
    try:
        return json.loads(respuesta_modelo)
    except:
        print("⚠️ El modelo no devolvió un JSON válido.")
        return []
