import re

def clasificar_intencion(texto: str) -> dict:
    texto = texto.lower().strip()

    # Sinónimos comunes para empleado
    patron_empleado = r"(emplead[oa]|trabajador[a]?)\s*\d+"

    # Detectar intención de ratio por mención explícita
    if re.search(patron_empleado, texto):
        return {
            "intencion": "empleado",
            "tiene_fecha": bool(re.search(r"\d{1,2} de [a-z]+ de \d{4}", texto)),
            "comentario": "Detectado patrón de empleado"
        }

    if re.search(r"(ratio|indicador|rendimiento|productividad)", texto):
        return {
            "intencion": "general",
            "tiene_fecha": bool(re.search(r"\d{1,2} de [a-z]+ de \d{4}", texto)),
            "comentario": "Consulta general de indicadores"
        }

    return {
        "intencion": "general",
        "tiene_fecha": False,
        "comentario": "Respuesta no interpretable"
    }

