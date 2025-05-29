import pandas as pd
from rapidfuzz import fuzz
from google_sheets_session import cargar_hoja_google_sheets


def extraer_nombre_producto(texto_usuario: str) -> str:
    """
    Extrae el nombre más probable de producto a partir del texto de entrada del usuario.
    Usa coincidencia difusa con columnas 'nombre' y 'aliases'.
    """
    try:
        # Cargar hoja de productos
        df = cargar_hoja_google_sheets("productos_catalogo")
        df.columns = [col.lower().strip().replace(" ", "_") for col in df.columns]
        print("📋 Columnas normalizadas:", df.columns.tolist())

        # Validar columnas necesarias
        if 'nombre' not in df.columns or 'aliases' not in df.columns:
            print("❌ Columnas requeridas faltantes en la hoja de productos")
            return None

        # Rellenar vacíos
        df['nombre'] = df['nombre'].fillna("")
        df['aliases'] = df['aliases'].fillna("")

        # Preparar lista de comparación
        candidatos = []
        for idx, row in df.iterrows():
            nombre = row['nombre'].strip().lower()
            aliases = [alias.strip().lower() for alias in row['aliases'].split(',') if alias.strip()] if row['aliases'] else []
            opciones = [nombre] + aliases

            for op in opciones:
                puntuacion = fuzz.partial_ratio(op, texto_usuario.lower())
                candidatos.append((puntuacion, nombre))

        if not candidatos:
            print("⚠️ No se encontraron candidatos en el catálogo de productos")
            return None

        # Obtener mejor coincidencia
        candidatos.sort(reverse=True)
        mejor_score, mejor_nombre = candidatos[0]
        print(f"🔍 Mejor coincidencia: '{mejor_nombre}' con puntuación {mejor_score}")

        # Umbral de confianza mínima
        if mejor_score >= 70:
            return mejor_nombre
        else:
            print("⚠️ Puntuación insuficiente para determinar un producto con confianza")
            return None

    except Exception as e:
        print(f"❌ Error al procesar productos: {e}")
        return None
