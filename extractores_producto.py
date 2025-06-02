
import re
from unidecode import unidecode

def extraer_nombre_producto(texto: str) -> str:
    '''
    Extrae el nombre probable del producto del texto proporcionado por el usuario.
    Se eliminan palabras comunes y se normaliza el texto para comparaciones más efectivas.
    '''
    texto = texto.lower()
    texto = unidecode(texto)

    # Palabras comunes a eliminar
    palabras_excluir = [
        'podrias', 'puedes', 'quiero', 'quisiera', 'me', 'informacion',
        'explicarme', 'explicar', 'modo', 'como', 'aplicar', 'producto',
        'del', 'de', 'el', 'la', 'los', 'las', 'un', 'una', 'sobre', 'acerca'
    ]

    # Eliminar signos de puntuación y dividir en palabras
    palabras = re.findall(r'\b\w+\b', texto)
    palabras_filtradas = [p for p in palabras if p not in palabras_excluir]

    # Reconstruir texto limpio
    return ' '.join(palabras_filtradas).strip()
