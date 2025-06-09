import re
import logging

logger = logging.getLogger(__name__)

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

    # ✅ NUEVO BLOQUE: detectar intención de explicar KPI o ratio
    if any(palabra in texto for palabra in ["qué es", "define", "definición de", "explica"]):
        return {
            "intencion": "kpi",
            "tiene_fecha": False,
            "comentario": "Detectada intención de explicar un KPI o ratio"
        }

    # Detectar intención de producto
    if any(palabra in texto for palabra in [
        "glatt", "producto", "alisador", "tratamiento", "beneficio", "cómo se usa", "opiniones", "comentarios", "hidrata", "schwarzkopf"
    ]):
        return {
            "intencion": "explicar_producto",
            "tiene_fecha": False,
            "comentario": "Consulta sobre un producto o sus beneficios"
        }

    return {
        "intencion": "general",
        "tiene_fecha": False,
        "comentario": "Respuesta no interpretable"
    }

    return {'intencion': 'kpi', 'comentario': 'Detectada intención de explicar un KPI o ratio'}

