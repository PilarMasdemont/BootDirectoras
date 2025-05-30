# productos.py

def explicar_producto(nombre_producto: str) -> str:
    productos = {
        "Keratina Orgánica": "Es un tratamiento sin formol que alisa y nutre el cabello con ingredientes naturales.",
        "Botox Capilar": "Hidratación profunda que repara la fibra capilar y devuelve brillo y suavidad.",
        "Colágeno Vegetal": "Fortalece el cabello y aporta elasticidad gracias a sus proteínas vegetales."
    }

    descripcion = productos.get(nombre_producto)

    if descripcion:
        return f"🧴 {nombre_producto}: {descripcion}"
    else:
        return f"No tengo información registrada para el producto '{nombre_producto}'. ¿Podrías verificar el nombre?"

