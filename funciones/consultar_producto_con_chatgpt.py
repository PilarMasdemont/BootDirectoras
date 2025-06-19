import json

PRODUCTOS_PATH = "Archivos_estaticos/productos_diccionario.json"

def cargar_productos():
    with open(PRODUCTOS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

PRODUCTOS = cargar_productos()

def consultar_producto_chatgpt(nombre_producto: str, atributo_duda: str = None) -> str:
    nombre = nombre_producto.lower().strip()

    # Buscar coincidencia exacta o parcial
    coincidencia = next(
        (key for key in PRODUCTOS if nombre == key.lower()), None
    ) or next(
        (key for key in PRODUCTOS if nombre in key.lower()), None
    )

    if not coincidencia:
        return f"No tengo información sobre el producto **{nombre_producto}** en la base de datos."

    info_producto = PRODUCTOS[coincidencia]

    if atributo_duda:
        atributo = atributo_duda.lower()
        resultados = []

        for subtitulo, descripcion in info_producto.items():
            lineas = descripcion.split("\n")
            filtrado = "\n".join(l for l in lineas if atributo in l.lower())
            if filtrado.strip():
                resultados.append(f"**{subtitulo}**:\n{filtrado}")

        if resultados:
            return f"**{coincidencia}** – Resultados sobre *{atributo_duda}*:\n\n" + "\n\n".join(resultados)
        else:
            resumen = ", ".join(info_producto.keys())
            return f"No encontré detalles sobre *{atributo_duda}* en **{coincidencia}**. Secciones disponibles: {resumen}"

    # Si no se pide un atributo, devolver todo
    partes = [f"**{coincidencia}**"]
    for subtitulo, descripcion in info_producto.items():
        partes.append(f"**{subtitulo}**:\n{descripcion.strip()}")

    return "\n\n".join(partes)




