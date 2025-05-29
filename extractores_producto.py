from rapidfuzz import process, fuzz
import pandas as pd

# 👉 Reemplaza esto por tu lógica de acceso a Google Sheets
def cargar_aliases_productos() -> pd.DataFrame:
    # Simulado: reemplaza con conexión real a tu Google Sheet
    return pd.read_csv("productos_catalogo.csv")  # o usa cargar_hoja_por_nombre(...)

def extraer_nombre_producto(texto_usuario: str) -> str:
    texto_usuario = texto_usuario.lower().strip()
    productos_df = cargar_aliases_productos()

    # Asegurarse de que no hay NaN
    productos_df["nombre"] = productos_df["nombre"].fillna("")
    productos_df["aliases"] = productos_df.get("aliases", "").fillna("")

    nombres = productos_df["nombre"].tolist()
    nombres_lower = [n.lower().strip() for n in nombres]

    # 🎯 Paso 1: Fuzzy match contra nombres oficiales
    mejor_match, score, _ = process.extractOne(texto_usuario, nombres_lower, scorer=fuzz.partial_ratio)
    if score >= 80:
        logging.info(f"[FUZZY MATCH] '{texto_usuario}' ≈ '{mejor_match}' (score={score})")
        return productos_df.iloc[nombres_lower.index(mejor_match)]["nombre"]

    # 🎯 Paso 2: Coincidencia directa contra aliases
    for _, row in productos_df.iterrows():
        alias_raw = str(row["aliases"]).lower()
        alias_list = [a.strip() for a in alias_raw.split(",") if a.strip()]
        if any(alias in texto_usuario for alias in alias_list):
            logging.info(f"[ALIAS MATCH] '{texto_usuario}' contiene alias '{alias_list}'")
            return row["nombre"]

    logging.warning(f"[NO MATCH] No se detectó producto para '{texto_usuario}'")
    return None
