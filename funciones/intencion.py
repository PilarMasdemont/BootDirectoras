import os
import openai

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clasificar_intencion(mensaje_usuario: str) -> str:
    prompt = (
        "Clasifica este mensaje de una directora con una sola palabra: 'general', 'empleados' o 'empleado'.\n\n"
        f"Mensaje: '{mensaje_usuario}'\n\n"
        "Reglas:\n"
        "- Devuelve 'general' si se pide un análisis global del salón, sin mención de personas ni códigos de empleado.\n"
        "- Devuelve 'empleados' si se refiere al análisis de todos los trabajadores, como 'los empleados', 'el personal', 'cada uno', 'cómo lo hicieron todos'.\n"
        "- Devuelve 'empleado' si menciona un trabajador concreto, por código (ej. 'empleado 42') o por nombre.\n\n"
        "Tu respuesta debe ser únicamente una de estas tres palabras: general, empleados, empleado."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip().lower()
