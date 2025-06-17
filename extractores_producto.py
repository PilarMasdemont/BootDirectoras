import pandas as pd
from rapidfuzz import fuzz
from sheets_io import cargar_hoja_por_nombre

SHEET_PRODUCTOS_ID = "1GcTc0MJsLE-UKS1TylYkn8qF_wjurxV2pKfGbugtb5M"
PESTANA_PRODUCTOS = "ProductosBoot"

def extraer_nombre_producto(texto_usuario: str) -> str:
    try:
        productos_df = cargar_hoja_por_nombre(SHEET_PRODUCTOS_ID, PESTANA_PRODUCTOS)
    except Exception as e:
        print("❌ Error al cargar hoja de productos:", e)
        return ""

    if productos_df.empty:
        return ""

    productos_df.columns = [col.lower().strip().replace(" ", "_") for col in productos_df.columns]

    if "nombre" not in productos_df.columns or "aliases" not in productos_df.columns:
        return ""

    productos_df["nombre"] = productos_df["nombre"].fillna("").str.strip()
    productos_df["aliases"] = productos_df["aliases"].fillna("").str.strip()

    mejor_score = 0
    mejor_nombre = ""

    for _, fila in productos_df.iterrows():
        nombre = fila["nombre"]
        aliases = fila["aliases"].split(",") if fila["aliases"] else []
        candidatos = [nombre] + [alias.strip() for alias in aliases]

        for candidato in candidatos:
            score = fuzz.partial_ratio(candidato.lower(), texto_usuario.lower())
            if score > mejor_score:
                mejor_score = score
                mejor_nombre = nombre

    return mejor_nombre if mejor_score >= 80 else ""


def explicar_producto(nombre_producto: str) -> str:
    try:
        productos_df = cargar_hoja_por_nombre(SHEET_PRODUCTOS_ID, PESTANA_PRODUCTOS)
    except Exception as e:
        print("❌ Error al cargar hoja de productos para explicación:", e)
        return "Hubo un problema al acceder a los datos del producto."

    productos_df.columns = [col.lower().strip().replace(" ", "_") for col in productos_df.columns]
    fila = productos_df[productos_df["nombre"].str.lower() == nombre_producto.lower()]

    if fila.empty:
        return f"No encontré información detallada sobre '{nombre_producto}'."

    fila = fila.iloc[0]
    beneficios = "\n".join([f"- {fila.get(col)}" for col in ["beneficio_1", "beneficio_2", "beneficio_3", "beneficio_4"] if pd.notna(fila.get(col))])
    modo_uso = fila.get("modo_uso", "No especificado")
    ingredientes = fila.get("ingredientes", "No especificado")

    respuesta = (
        f"🧴 *{nombre_producto}* es un producto con los siguientes beneficios:\n{beneficios}\n\n"
        f"📌 *Modo de uso:* {modo_uso}\n"
        f"🧪 *Ingredientes:* {ingredientes}"
    )

    return respuesta


