import json
import re

PRODUCTOS_PATH = "Archivos_estaticos/productos_diccionario.json"

def normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = re.sub(r"[^\w\sáéíóúüñ]", "", texto)  # eliminar puntuación
    texto = re.sub(r"\b\d+\s?(ml|g|gr|kg|l|litros)?\b", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

with open(PRODUCTOS_PATH, "r", encoding="utf-8") as f:
    PRODUCTOS_JSON = json.load(f)
    PRODUCTOS_NORMALIZADOS = {
        normalizar(nombre): nombre for nombre in PRODUCTOS_JSON.keys()
    }

def extraer_nombre_producto(texto_usuario: str) -> str:
    texto_normalizado = normalizar(texto_usuario)

    for nombre_normalizado, original in PRODUCTOS_NORMALIZADOS.items():
        if nombre_normalizado in texto_normalizado:
            return original

    return ""  # No se encontró

def explicar_producto(nombre_producto: str) -> str:
    producto = PRODUCTOS_JSON.get(nombre_producto)
    if not producto:
        return f"No encontré información detallada sobre '{nombre_producto}'."

    partes = [f"🧴 *{nombre_producto}*"]

    for subtitulo, contenido in producto.items():
        partes.append(f"**{subtitulo.capitalize()}**:\n{contenido.strip()}")

    return "\n\n".join(partes)



