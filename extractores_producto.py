import pandas as pd
from rapidfuzz import fuzz
from sheets_io import cargar_hoja_por_gid

SHEET_PRODUCTOS_ID = "1GcTc0MJsLE-UKS1TylYkn8qF_wjurxV2pKfGbugtb5M"
GID_PRODUCTOS = "0"

def extraer_nombre_producto(texto_usuario: str) -> dict:
    print(f"🔍 Buscando producto en texto: '{texto_usuario}'")

    try:
        productos_df = cargar_hoja_por_gid(SHEET_PRODUCTOS_ID, GID_PRODUCTOS)
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
        return {"nombre_producto": mejor_nombre, "comentario": "Coincidencia encontrada"}
    else:
        print(f"❌ No se encontró coincidencia suficiente. Mejor score: {mejor_score}")
        return {"nombre_producto": "PRODUCTO_NO_ENCONTRADO", "comentario": "No se identificó el producto"}


