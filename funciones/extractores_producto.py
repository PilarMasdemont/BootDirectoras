import json

# Cargar diccionario de alias desde alias_productos.json
with open("Archivos_estaticos/alias_productos.json", "r", encoding="utf-8") as f:
    ALIASES_PRODUCTOS = json.load(f)

def extraer_nombre_producto(texto: str) -> str:
    texto = texto.lower()
    for alias, real in ALIASES_PRODUCTOS.items():
        if alias in texto:
            return real
    return None

def extraer_duda_producto(texto: str) -> str:
    texto = texto.lower()
    posibles = [
        "beneficio", "para que", "para qué", "sirve", "uso", "cómo se usa", "instrucciones",
        "ingredientes", "composición", "resultados", "efectos", "modo de aplicación", "frecuencia"
    ]
    for p in posibles:
        if p in texto:
            return p
    return None




