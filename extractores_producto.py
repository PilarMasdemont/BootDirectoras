import re

def extraer_nombre_producto(texto: str) -> str:
    """
    Extrae el posible nombre de producto desde el texto del usuario,
    eliminando palabras innecesarias o muy comunes.
    """
    texto = texto.lower()
    patrones_irrelevantes = [
        r"\bproducto\b", r"\binformaci[oó]n\b", r"\bexplic[aá]me\b", r"\bsobre\b",
        r"\bmodo\b", r"\baplicar\b", r"\bel\b", r"\bla\b", r"\bdel\b", r"\bde\b",
    ]
    
    for patron in patrones_irrelevantes:
        texto = re.sub(patron, '', texto)
    
    texto = re.sub(r'\s+', ' ', texto).strip()  # Limpiar espacios
    return texto
