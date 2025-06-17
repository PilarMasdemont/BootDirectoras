import json

PRODUCTOS_PATH = "Archivos_estaticos/productos_diccionario.json"

def cargar_productos():
    with open(PRODUCTOS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

PRODUCTOS = cargar_productos()

def consultar_producto_chatgpt(nombre_producto: str, atributo_duda: str = None) -> str:
    nombre = nombre_producto.lower().strip()

    # Coincidencia flexible
    coincidencia = next((key for key in PRODUCTOS if nombre in key.lower()), None)
    if not coincidencia:
        return f"No tengo información sobre el producto **{nombre_producto}** en la base de datos."

    descripcion = PRODUCTOS[coincidencia]

    if atributo_duda:
        # Extraer bloques relevantes si se menciona algo como "ingredientes", "beneficios", etc.
        lineas = descripcion.split("\n")
        bloques = [l for l in lineas if atributo_duda.lower() in l.lower()]
        if bloques:
            return f"**{coincidencia}** – Resultado sobre *{atributo_duda}*:\n\n" + "\n".join(bloques)
        else:
            return f"No encontré detalles sobre *{atributo_duda}* en **{coincidencia}**, pero aquí tienes toda la información:\n\n{descripcion}"

    return f"**{coincidencia}**\n\n{descripcion}"



