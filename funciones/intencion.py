import openai
import os

# Obtener la clave desde variables de entorno
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise EnvironmentError("❌ Falta la variable de entorno OPENAI_API_KEY")

openai.api_key = api_key

def clasificar_intencion(mensaje_usuario: str) -> str:
    prompt = (
        "Dado este mensaje de una directora:\n"
        f"'{mensaje_usuario}'\n"
        "Devuelve solo una palabra: 'general' si pide una explicación general del salón,\n"
        "o 'individual' si quiere un desglose por trabajador."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip().lower()

