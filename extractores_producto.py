# extractores_producto.py

import pandas as pd
from rapidfuzz import fuzz
from google_sheets_session import cargar_aliases_productos

def extraer_nombre_producto(texto_usuario: str) -> dict:
    """
    Intenta identificar el nombre de un producto en el texto del usuario usando
    coincidencia exacta, alias y similitud con rapidfuzz.
    """
    try:
        print(f"🔍 Buscando producto en texto: '{texto_usuario}'")

        productos_df = cargar_aliases_productos()
        if productos_df.empty:
            raise ValueError("El DataFrame de productos está vacío")

        # Asegurar columnas necesarias
        for col in ["nombre", "aliases"]:
            if col not in productos_df.columns:
                raise KeyError(f"La columna '{col}' no está en la hoja de productos")

        # Preprocesamiento
        texto_usuario = texto_usuario.lower().strip()
        productos_df["nombre"] = productos_df["nombre"].fillna("").str.lower()
        productos_df["aliases"] = productos_df["aliases"].fillna("").str.lower()

        # Búsqueda exacta en nombres y alias
        for _, fila in productos_df.iterrows():
            nombre = fila["nombre"]
            aliases = [a.strip() for a in fila["aliases"].split(",") if a.strip()]
            if nombre in texto_usuario or any(alias in texto_usuario for alias in aliases):
                print(f"✅ Coincidencia exacta: {nombre}")
                return {"nombre_producto": nombre, "comentario": "Producto detectado (exacto)"}

        # Coincidencia difusa con rapidfuzz
        mejor_score = 0
        mejor_producto = None

        for _, fila in productos_df.iterrows():
            nombre = fila["nombre"]
            aliases = [a.strip() for a in fila["aliases"].split(",") if a.strip()]
            scores = [fuzz.partial_ratio(texto_usuario, nombre)] + [fuzz.partial_ratio(texto_usuario, alias) for alias in aliases]
            max_score = max(scores)

            if max_score > mejor_score and max_score >= 80:  # umbral ajustable
                mejor_score = max_score
                mejor_producto = nombre

        if mejor_producto:
            print(f"🤖 Coincidencia por similitud: {mejor_producto} (score: {mejor_score})")
            return {"nombre_producto": mejor_producto, "comentario": "Producto detectado (similitud)"}

        # Si no se detecta nada
        print("⚠️ No se detectó un producto en el mensaje")
        return {"nombre_producto": "PRODUCTO_NO_ENCONTRADO", "comentario": "Respuesta no interpretable"}

    except Exception as e:
        print(f"❌ Error durante la extracción del nombre de producto: {e}")
        return {"nombre_producto": "PRODUCTO_NO_ENCONTRADO", "comentario": str(e)}

