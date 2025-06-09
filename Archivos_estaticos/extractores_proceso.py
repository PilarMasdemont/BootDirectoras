# Este módulo se encargará de extraer automáticamente el nombre del proceso y 
#la parte específica de la duda (como "duración", "pasos", etc.) desde el texto del usuario.


from difflib import get_close_matches

# Lista de procesos conocida (puedes cargarla dinámicamente si lo prefieres)
LISTA_PROCESOS = [
    "queratina",
    "mechas",
    "tratamientos en frio",
    "tratamientos frío y calor",
    "whatsapp consejo cabello",
    "quien se va",
    "niñas que hago",
    "inventario",
    "agenda",
    "turnos",
    "clientes",
    "caja",
    "pedidos",
    "satisfacción"
]

# Palabras clave que representan lo que el usuario quiere saber
DUDAS_COMUNES = [
    "duración",
    "pasos",
    "cómo se hace",
    "quién lo hace",
    "responsable",
    "materiales",
    "instrucciones",
    "qué se necesita",
    "orden",
    "funciona",
    "flujo",
    "procedimiento"
]

def extraer_nombre_proceso(texto: str) -> str:
    texto = texto.lower()
    coincidencias = get_close_matches(texto, LISTA_PROCESOS, n=1, cutoff=0.4)
    return coincidencias[0] if coincidencias else None

def extraer_duda_proceso(texto: str) -> str:
    texto = texto.lower()
    for duda in DUDAS_COMUNES:
        if duda in texto:
            return duda
    return None
