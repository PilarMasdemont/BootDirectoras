
import re

def normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = re.sub(r"[^a-záéíóúüñ0-9\s]", "", texto)
    texto = re.sub(r"\b\d+ml\b", "", texto)
    return texto.strip()

def clasificar_intencion_completa(texto: str) -> dict:
    print("🛠️ FUNCION clasificar_intencion_completa ACTIVADA")
    print(f"📩 Mensaje recibido: {texto}")
    print(f"🧹 Texto normalizado: {normalizar(texto)}")

    return {
        "intencion": "debug",
        "comentario": "Esto es una prueba de despliegue de intencion_total",
        "tiene_fecha": False
    }







