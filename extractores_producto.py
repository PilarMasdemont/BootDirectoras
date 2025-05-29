import re
from rapidfuzz import process, fuzz
import pandas as pd

# 👇 Carga rápida del catálogo de productos
def cargar_nombres_productos() -> list:
    try:
        df = pd.read_csv("productos_catalogo.csv")  # o cargar_hoja_por_nombre(...)
        return [str(n).lower().strip() for n in df["nombre"].dropna().tolist()]
    except Exception as e:
        print(f"Error al cargar nombres de producto: {e}")
        return []

def clasificar_intencion(texto: str) -> dict:
    texto = texto.lower().strip()

    # 🎯 1. Palabras clave asociadas a productos
    palabras_producto = [
        "producto", "alisador", "tratamiento", "beneficio", "cómo se usa", "opiniones",
        "comentarios", "hidrata", "keratina", "ácido hialurónico", "glatt", "lisse", "color freeze"
    ]
    if any(p in texto for p in palabras_producto):
        return {
            "intencion": "explicar_producto",
            "tiene_fecha": False,
            "comentario": "Detectado por palabras clave de producto"
        }

    # 🎯 2. Fuzzy match contra nombres de producto
    nombres_producto = cargar_nombres_productos()
    if nombres_producto:
        mejor_match, score, _ = process.extractOne(texto, nombres_producto, scorer=fuzz.partial_ratio)
        if score >= 85:
            return {
                "intencion": "explicar_producto",
                "tiene_fecha": False,
                "comentario": f"Detectado por fuzzy match con producto: {mejor_match}"
            }

    # 3. Patrón de empleado
    patron_empleado = r"(emplead[oa]|trabajador[a]?)\s*\d+"
    if re.search(patron_empleado, texto):
        return {
            "intencion": "empleado",
            "tiene_fecha": bool(re.search(r"\d{1,2} de [a-z]+ de \d{4}", texto)),
            "comentario": "Detectado patrón de empleado"
        }

    # 4. Indicadores generales
    if re.search(r"(ratio|indicador|rendimiento|productividad)", texto):
        return {
            "intencion": "general",
            "tiene_fecha": bool(re.search(r"\d{1,2} de [a-z]+ de \d{4}", texto)),
            "comentario": "Consulta general de indicadores"
        }

    # 5. Sin coincidencias
    return {
        "intencion": "general",
        "tiene_fecha": False,
        "comentario": "Respuesta no interpretable"
    }
