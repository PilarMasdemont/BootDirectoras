import re
from pathlib import Path
from rapidfuzz import process, fuzz
import logging

def cargar_info_producto(nombre_producto: str) -> str:
    ruta = Path(__file__).parent.parent / "datos_estaticos" / "productos.md"

    if not ruta.exists():
        return f"No se encontró el archivo de productos en la ruta esperada: {ruta}"

    contenido = ruta.read_text(encoding="utf-8")

    # Extraer títulos de productos del markdown
    secciones = re.split(r"\n(?=##?\s)", contenido)
    titulos = [re.match(r"#+\s*(.*)", sec.strip()) for sec in secciones]
    titulos = [m.group(1).strip() for m in titulos if m]

    # Buscar mejores coincidencias con RapidFuzz
    resultados = process.extract(
        nombre_producto.lower(), titulos, scorer=fuzz.token_set_ratio, limit=5
    )
    logging.info(f"[MATCHING productos.md] Resultados para '{nombre_producto}': {resultados}")

    encontrados = [r for r in resultados if r[1] >= 50]
    if not encontrados:
        return f"No se ha encontrado información del producto '{nombre_producto}' en la base de datos."

    mejor_match = encontrados[0][0]

    # Extraer la sección correspondiente del markdown
    patron = re.compile(rf"(##.*{re.escape(mejor_match)}.*?)(?=\n##|\Z)", re.DOTALL | re.IGNORECASE)
    match = patron.search(contenido)
    if match:
        return match.group(1).strip()
    else:
        return f"No se ha podido extraer información para '{mejor_match}'."
