from pathlib import Path

# Código reconstruido de extractores_producto.py con la nueva lógica pero respetando lo anterior
codigo_reconstruido = '''
import re
import pandas as pd
from rapidfuzz import fuzz
from google_sheets_session import cargar_aliases_productos

def extraer_nombre_producto(texto: str) -> str:
    """
    Extrae el nombre del producto del mensaje del usuario utilizando coincidencia difusa
    con nombres y aliases de productos de Google Sheets.
    """
    texto = texto.lower().strip()
    productos_df = cargar_aliases_productos()

    # Normalizar columnas
    productos_df.columns = [str(c).strip().lower().replace(" ", "_") for c in productos_df.columns]
    productos_df["nombre"] = productos_df["nombre"].fillna("")
    productos_df["aliases"] = productos_df["aliases"].fillna("")

    mejor_coincidencia = {"producto": None, "score": 0}

    for _, fila in productos_df.iterrows():
        nombre = str(fila["nombre"]).lower()
        if not nombre:
            continue
        score_nombre = fuzz.partial_ratio(texto, nombre)
        if score_nombre > mejor_coincidencia["score"]:
            mejor_coincidencia = {"producto": nombre, "score": score_nombre}

        for alias in str(fila["aliases"]).split(","):
            alias = alias.strip().lower()
            if alias:
                score_alias = fuzz.partial_ratio(texto, alias)
                if score_alias > mejor_coincidencia["score"]:
                    mejor_coincidencia = {"producto": nombre, "score": score_alias}

    if mejor_coincidencia["score"] > 70:
        return mejor_coincidencia["producto"]
    return None

def clasificar_intencion(texto: str) -> dict:
    texto = texto.lower()

    patrones_explicar_producto = [
        r"beneficios.*producto", r"para qué sirve", r"cómo.*usar", r"modo.*de.*uso",
        r"cuál es el efecto", r"qué hace", r"explica.*producto", r"producto.*sirve"
    ]

    for patron in patrones_explicar_producto:
        if re.search(patron, texto):
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
'''

# Guardar el archivo reconstruido
ruta_final = Path("/mnt/data/extractores_producto_RECONSTRUIDO.py")
ruta_final.write_text(codigo_reconstruido)

ruta_final.name

