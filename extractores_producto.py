# extractores_producto.py
import pandas as pd

# Cargar lista de productos y aliases desde Google Sheet (simplificado)
# Aquí deberías conectar a Google Sheets con tu método ya usado
def cargar_aliases_productos():
    # Simulación: reemplaza con lectura real desde Google Sheets
    data = {
        "nombre": ["Strait Styling Glatt", "Color Freeze"],
        "aliases": ["glatt, alisador schwarzkopf", "color freeze, freeze"],
    }
    return pd.DataFrame(data)

def extraer_nombre_producto(texto_usuario: str) -> str:
    texto_usuario = texto_usuario.lower()
    productos_df = cargar_aliases_productos()

    for _, row in productos_df.iterrows():
        alias_lista = [a.strip() for a in row["aliases"].split(",")]
        for alias in alias_lista:
            if alias in texto_usuario:
                return row["nombre"]
    return None
