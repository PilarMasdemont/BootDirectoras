import os
import openai

# Crea una instancia del cliente moderno
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clasificar_intencion(mensaje_usuario: str) -> str:
    prompt = (
        "Dado este mensaje de una directora:\n"
        f"'{mensaje_usuario}'\n"
        "Devuelve solo una palabra: 'general' si pide una explicación general del salón,\n"
        "o 'individual' si quiere un desglose por trabajador."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip().lower()
