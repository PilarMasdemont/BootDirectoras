import logging
from pathlib import Path
from rapidfuzz import process, fuzz

def cargar_info_producto(nombre_producto: str) -> str:
    ruta = Path(__file__).resolve().parent.parent / "datos_estaticos" / "productos.md"
    logging.info(f"📁 Ruta absoluta del archivo productos.md: {ruta}")

    if not ruta.exists():
        logging.warning("⚠️ Archivo productos.md no encontrado.")
        return "Lo siento, no he podido encontrar el archivo de productos."

    contenido = ruta.read_text(encoding="utf-8")

    lineas = contenido.splitlines()
    indices_titulos = [(i, linea.strip()) for i, linea in enumerate(lineas) if linea.startswith("### ")]

    titulos = [titulo[1][4:].strip() for titulo in indices_titulos]

    resultados = process.extract(
        nombre_producto, titulos, scorer=fuzz.partial_ratio, limit=3
    )
    logging.info(f"🔍 Resultados de matching: {resultados}")

    mejor_match = resultados[0] if resultados else None

    if mejor_match and mejor_match[1] > 40:
        logging.info(f"✅ Producto encontrado: {mejor_match[0]} con similitud {mejor_match[1]:.2f}")
        index_encontrado = next(i for i, (_, t) in enumerate(indices_titulos) if t[4:].strip() == mejor_match[0])
        inicio = indices_titulos[index_encontrado][0]
        fin = indices_titulos[index_encontrado + 1][0] if index_encontrado + 1 < len(indices_titulos) else len(lineas)
        descripcion = "\n".join(lineas[inicio:fin]).strip()
        return descripcion
    else:
        sugerencias = [r[0] for r in resultados if r[1] > 25]
        if sugerencias:
            logging.info(f"🤔 No coincidencia exacta, pero sugerencias: {sugerencias}")
            sugerencias_texto = "\n".join([f"- {s}" for s in sugerencias])
            return (
                f"No he encontrado una coincidencia exacta para '{nombre_producto}', "
                "pero quizás te refieras a:\n" + sugerencias_texto
            )
        else:
            logging.warning("❌ Ningún producto suficientemente parecido encontrado.")
            return (
                f"No he encontrado información relevante sobre el producto '{nombre_producto}'. "
                "Por favor, verifica el nombre o proporciona más detalles."
            )
