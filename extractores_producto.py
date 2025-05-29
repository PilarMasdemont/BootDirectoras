import re
import pandas as pd
from rapidfuzz import process, fuzz

# 👇 Carga catálogo para fuzzy match en intenciones
def cargar_nombres_productos() -> list:
    try:
        df = pd.read_csv("productos_catalogo.csv")
        return [str(n).lower().strip() for n in df["nombre"].dropna().tolist()]
    except Exception as e:
        print(f"Error al cargar nombres de producto: {e}")
        return []

# 🎯 Fuzzy detection para intenciones
def clasificar_intencion(texto: str) -> dict:
    texto = texto.lower().strip()

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

    nombres_producto = cargar_nombres_productos()
    if nombres_producto:
        mejor_match, score, _ = process.extractOne(texto, nombres_producto, scorer=fuzz.partial_ratio)
        if score >= 85:
            return {
                "intencion": "explicar_producto",
                "tiene_fecha": False,
                "comentario": f"Detectado por fuzzy match con producto: {mejor_match}"
            }

    patron_empleado = r"(emplead[oa]|trabajador[a]?)\s*\d+"
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

# ✅ DETECCIÓN DEL PRODUCTO
def cargar_aliases_productos() -> pd.DataFrame:
    try:
        df = pd.read_csv("productos_catalogo.csv")
        return df
    except Exception as e:
        print(f"Error al cargar hoja de productos: {e}")
        return pd.DataFrame()

def extraer_nombre_producto(texto_usuario: str) -> str:
    texto_usuario = texto_usuario.lower().strip()
    productos_df = cargar_aliases_productos()

    productos_df["nombre"] = productos_df["nombre"].fillna("")
    productos_df["aliases"] = productos_df.get("aliases", "").fillna("")

    nombres = productos_df["nombre"].tolist()
    nombres_lower = [n.lower().strip() for n in nombres]

    mejor_match, score, _ = process.extractOne(texto_usuario, nombres_lower, scorer=fuzz.partial_ratio)
    if score >= 80:
        return productos_df.iloc[nombres_lower.index(mejor_match)]["nombre"]

    for _, row in productos_df.iterrows():
        alias_raw = str(row["aliases"]).lower()
        alias_list = [a.strip() for a in alias_raw.split(",") if a.strip()]
        if any(alias in texto_usuario for alias in alias_list):
            return row["nombre"]

    return None
