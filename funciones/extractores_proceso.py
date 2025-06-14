# Este módulo se encargará de extraer automáticamente el nombre del proceso y 
# la parte específica de la duda (como "duración", "pasos", etc.) desde el texto del usuario.

import json
from unidecode import unidecode

with open("Archivos_estaticos/alias_procesos.json", "r", encoding="utf-8") as f:
    ALIASES_PROCESOS = json.load(f)

def normalizar(texto: str) -> str:
    return unidecode(texto.lower().strip())

def extraer_nombre_proceso_desde_alias(texto_usuario: str) -> str:
    texto_norm = normalizar(texto_usuario)
    for alias, nombre_proceso in ALIASES_PROCESOS.items():
        if normalizar(alias) in texto_norm:
            return nombre_proceso
    return None

def extraer_nombre_proceso(texto: str) -> str:
    texto = texto.lower()
    procesos = [
        "queratina", "mechas", "agenda", "turnos", "inventario", "tratamiento", "clientes",
        "satisfacción", "citas", "caja", "cerrar caja", "pedidos", "manual", "lavado", 
        "asesoramiento", "cerrar día", "apertura", "productos", "stock", "color", 
        "organización", "bienvenida", "revisión"
    ]
    for proceso in procesos:
        if proceso in texto:
            return proceso
    return ""










