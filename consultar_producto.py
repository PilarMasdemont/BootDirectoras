# funciones/consultar_producto.py

import json

PRODUCTOS_PATH = "Archivos_estaticos/productos_diccionario.json"

with open(PRODUCTOS_PATH, "r", encoding="utf-8") as f:
    PRODUCTOS = json.load(f)

def consultar_producto(nombre_producto: str, atributo: str = None) -> str:
    producto_info = PRODUCTOS.get(nombre_producto)

    if not producto_info:
        return f"No tengo información sobre **{nombre_producto}**."

    if atributo:
        # Buscar dentro de las secciones del producto
        resultados = []
        for subtitulo, contenido in producto_info.items():
            if atributo.lower() in subtitulo.lower() or atributo.lower() in contenido.lower():
                resultados.append(f"**{subtitulo}**:\n{contenido.strip()}")

        if resultados:
            return f"🧴 *{nombre_producto}* – Información sobre *{atributo}*:\n\n" + "\n\n".join(resultados)
        else:
            disponibles = ", ".join(producto_info.keys())
            return f"No encontré información sobre *{atributo}* en **{nombre_producto}**. Secciones disponibles: {disponibles}."

    # Si no hay atributo, devolver toda la información del producto
    partes = [f"🧴 *{nombre_producto}*"]
    for subtitulo, contenido in producto_info.items():
        partes.append(f"**{subtitulo}**:\n{contenido.strip()}")

    return "\n\n".join(partes)

