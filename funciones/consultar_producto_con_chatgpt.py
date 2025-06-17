import json

PRODUCTOS_PATH = "Archivos_estaticos/productos_diccionario.json"

def cargar_productos():
    with open(PRODUCTOS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

PRODUCTOS = cargar_productos()

def consultar_producto_chatgpt(nombre_producto: str, atributo_duda: str = None) -> str:
    nombre = nombre_producto.lower().strip()

    # Buscar coincidencia flexible
    coincidencia = next(
        (key for key in PRODUCTOS if nombre == key.lower()),
        None
    ) or next(
        (key for key in PRODUCTOS if nombre in key.lower()),
         None
    )

    if not coincidencia:
        return f"No tengo información sobre el producto **{nombre_producto}** en la base de datos."

    info_producto = PRODUCTOS[coincidencia]

    # Atributo específico
    if atributo_duda:
        atributo = atributo_duda.lower()
        resultados = []

        for presentacion, detalles in info_producto.items():
            lineas = detalles.split("\n")
            bloque_filtrado = "\n".join(l for l in lineas if atributo in l.lower())
            if bloque_filtrado.strip():
                resultados.append(f"**{presentacion}**:\n{bloque_filtrado}")

        if resultados:
            return f"**{coincidencia}** - Resultados sobre *{atributo_duda}*:\n\n" + "\n\n".join(resultados)
        else:
            resumen = "\n".join(f"- {k}" for k in info_producto)
            return f"No encontré detalles sobre *{atributo_duda}* en **{coincidencia}**. Presentaciones disponibles: {resumen}"

    # Mostrar todo el contenido por tamaño
    partes = [f"**{coincidencia}**"]
    for presentacion, descripcion in info_producto.items():
        partes.append(f"**{presentacion}**:\n{descripcion}")
    return "\n\n".join(partes)


