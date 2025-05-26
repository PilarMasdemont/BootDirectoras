import os
import openai

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clasificar_intencion(mensaje_usuario: str) -> str:
    prompt = (
        "Clasifica el siguiente mensaje de una directora con una sola palabra: 'general' o 'individual'.\n\n"
        f"Mensaje: '{mensaje_usuario}'\n\n"
        "Reglas:\n"
        "- Devuelve 'general' si el mensaje pide una explicación agregada o global del salón, como 'cómo fue el día', 'resultado del salón', 'cómo fue el salón 1 el 23 de mayo'.\n"
        "- Devuelve 'individual' si el mensaje se refiere a trabajadores, empleados, personal, nombres concretos, códigos de empleado, o usa frases como 'cada uno', 'por trabajador', 'los empleados', 'empleado 95', etc.\n\n"
        "Respuesta:"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip().lower()
