import json
import os

# Asegúrate de que este path apunte correctamente al archivo JSON cargado
PRODUCTOS_PATH = "Archivos_estaticos/productos_diccionario.json"

def cargar_productos():
    with open(PRODUCTOS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

PRODUCTOS = cargar_productos()

def consultar_producto_chatgpt(nombre_producto: str, atributo_duda: str = None) -> str:
    nombre_buscado = nombre_producto.strip().lower()

    # Buscar nombre ignorando mayúsculas
    producto = None
    nombre_real = None
    for nombre_real_candidato in PRODUCTOS:
        if nombre_real_candidato.lower() == nombre_buscado:
            nombre_real = nombre_real_candidato
            producto = PRODUCTOS[nombre_real]
            break

    if not producto:
        return f"No tengo información sobre el producto **{nombre_producto}** en la base de datos."

    if atributo_duda:
        atributo = atributo_duda.lower()
        coincidencias = [clave for clave in producto if atributo in clave.lower()]
        if coincidencias:
            respuesta = producto[coincidencias[0]]
            return f"Sobre **{nombre_real}**, esto es lo que encontré sobre *{coincidencias[0]}*:\n\n{respuesta}"
        else:
            return f"No encontré información específica sobre *{atributo_duda}* en **{nombre_real}**. Pero esto es lo que tengo:\n\n{json.dumps(producto, indent=2, ensure_ascii=False)}"

    # Sin atributo → responder todo el contenido del producto
    partes = [f"**{nombre_real}**"]
    for clave, valor in producto.items():
        partes.append(f"- **{clave.capitalize()}**: {valor}")
    return "\n".join(partes)

