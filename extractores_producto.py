import pandas as pd
from rapidfuzz import fuzz
from sheets_io import cargar_hoja_por_nombre

SHEET_PRODUCTOS_ID = "1GcTc0MJsLE-UKS1TylYkn8qF_wjurxV2pKfGbugtb5M"
PESTANA_PRODUCTOS = "ProductosBoot"

def extraer_nombre_producto(texto_usuario: str) -> dict:
    print(f"🔍 Buscando producto en texto: '{texto_usuario}'")

    try:
        productos_df = cargar_hoja_por_nombre(SHEET_PRODUCTOS_ID, PESTANA_PRODUCTOS)
        print("📋 Columnas originales:", productos_df.columns.tolist())
    except Exception as e:
        print("❌ Error al cargar hoja de productos:", e)
        return {"nombre_producto": "PRODUCTO_NO_ENCONTRADO", "comentario": "Error al acceder a los datos"}

    if productos_df.empty:
        print("❌ El DataFrame de productos está vacío")
        return {"nombre_producto": "PRODUCTO_NO_ENCONTRADO", "comentario": "Catálogo vacío o inaccesible"}

    # Normalizar columnas
    productos_df.columns = [col.lower().strip().replace(" ", "_") for col in productos_df.columns]
    print("📋 Columnas normalizadas:", productos_df.columns.tolist())

    # Verificar columnas requeridas
    if "nombre" not in productos_df.columns or "aliases" not in productos_df.columns:
        print("❌ Faltan columnas requeridas: 'nombre' y/o 'aliases'")
        return {"nombre_producto": "PRODUCTO_NO_ENCONTRADO", "comentario": "Estructura de hoja inválida"}

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
            print(f"🔎 Evaluando: '{candidato}' vs. '{texto_usuario}' → score: {score}")
            if score > mejor_score:
                mejor_score = score
                mejor_nombre = nombre

    if mejor_score >= 80:
        print(f"✅ Producto encontrado: {mejor_nombre} (score: {mejor_score})")
        # Llamar a la función de explicación directamente para completar el flujo
        explicacion = explicar_producto(mejor_nombre)
        return {"nombre_producto": mejor_nombre, "comentario": "Coincidencia encontrada", "respuesta": explicacion}
    else:
        print(f"❌ No se encontró coincidencia suficiente. Mejor score: {mejor_score}")
        return {"nombre_producto": "PRODUCTO_NO_ENCONTRADO", "comentario": "No se identificó el producto"}

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


