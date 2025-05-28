import os
import openai
import re

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clasificar_intencion(mensaje_usuario: str) -> dict:
    prompt = (
        "Clasifica este mensaje con una estructura JSON.\n\n"
        "Debe incluir:\n"
        "- intencion: 'general', 'empleados', o 'empleado'\n"
        "- tiene_fecha: true o false si el mensaje contiene una fecha explícita\n"
        "- comentario: breve explicación del motivo\n\n"
        f"Mensaje: '{mensaje_usuario}'\n\n"
        "Reglas:\n"
        "- Usa 'general' si se analiza un salón sin mencionar empleados.\n"
        "- Usa 'empleados' si habla de varios trabajadores.\n"
        "- Usa 'empleado' si menciona uno solo, por código o nombre.\n"
        "- Considera que hay fecha si se menciona día, mes y opcionalmente año.\n\n"
        "Ejemplo de respuesta:\n"
        "{\"intencion\": \"empleado\", \"tiene_fecha\": true, \"comentario\": \"Se refiere a un empleado específico con fecha\"}"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    try:
        return eval(response.choices[0].message.content.strip())
    except:
        return {"intencion": "general", "tiene_fecha": False, "comentario": "Respuesta no interpretable"}

