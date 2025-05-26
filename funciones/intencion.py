import os
import openai

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clasificar_intencion(mensaje_usuario: str) -> str:
    prompt = (
        "Eres una herramienta de clasificación de intención para mensajes de directoras de salón.\n"
        "Dado el siguiente mensaje:\n"
        f"'{mensaje_usuario}'\n\n"
        "Clasifica con una sola palabra:\n"
        "- Devuelve 'general' si piden una explicación del resultado global del salón (por ejemplo, 'resultado del día', 'cómo fue el día', 'salón 1').\n"
        "- Devuelve 'individual' si el mensaje menciona trabajadores, empleados, nombres concretos, o se interesa por el rendimiento de una persona (por ejemplo, 'empleado 8', 'Sandra', 'cada trabajador').\n\n"
        "Tu respuesta debe ser SOLO una palabra: 'general' o 'individual'."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip().lower()
