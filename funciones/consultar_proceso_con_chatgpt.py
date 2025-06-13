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

    for key_norm, original_key in claves_lower.items():
        if nombre_norm in key_norm or key_norm in nombre_norm:
            return original_key

    return None

def consultar_proceso_chatgpt(nombre_proceso: str, pregunta_usuario: str) -> str:
    nombre_normalizado = normalizar(nombre_proceso)

    # 🔍 Buscar varios procesos si es algo general como "tratamiento"
    if "tratamiento" in nombre_normalizado:
        procesos_relacionados = {
            k: v for k, v in PROCESOS.items() if "tratamiento" in normalizar(k)
        }

        if not procesos_relacionados:
            return "❗️No encontré procesos relacionados con tratamientos."

        contenido_multiple = "\n\n".join(
            [f"Proceso: {k}\n{v}" for k, v in procesos_relacionados.items()]
        )

        prompt = f"""
Eres Mont Dirección, una asistente experta en gestión de salones de belleza. Estas repsondiendo a una de las peluqueras del salón.

A continuación tienes el contenido completo del proceso llamado **{proceso_clave}**:

\"\"\"
{contenido_multiple}
\"\"\"

Tu tarea es responder a la siguiente duda planteada por la peluquera:

**{pregunta_usuario}**
  
Solo responde con lo que aparece en el contenido anterior, no des informacion que no aparezca en los documentos, reordenado de forma clara.

"""
    else:
        proceso_clave = encontrar_proceso(nombre_proceso)
        if not proceso_clave:
            return f"❗️No encontré ningún proceso que se parezca a '{nombre_proceso}'."

        contenido = PROCESOS[proceso_clave]

        prompt = f"""
Eres Mont Dirección, una asistente experta en gestión de salones de belleza. Estas repsondiendo a una de las peluqueras del salón.

A continuación tienes el contenido completo del proceso llamado **{proceso_clave}**:

\"\"\"
{contenido}
\"\"\"

Una peluquera te ha preguntado lo siguiente:

**{pregunta_usuario}**
  
Solo responde con lo que aparece en el contenido anterior, no des informacion que no aparezca en los documentos, reordenado de forma clara.
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







