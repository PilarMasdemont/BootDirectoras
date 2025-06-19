import os
import json
from hashlib import md5
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

CARPETA_JSONS = "archivos_estaticos"
INDICE_PATH = "data/indice_docs.json"
HASH_PATH = "data/indice_hash.json"

def resumen_sumy(texto, n=1):
    parser = PlaintextParser.from_string(texto, Tokenizer("spanish"))
    resumen = LsaSummarizer()(parser.document, n)
    return " ".join(str(s) for s in resumen)

def calcular_hash_archivos(ruta_dir):
    archivos = sorted([f for f in os.listdir(ruta_dir) if f.endswith(".json")])
    return md5("".join(archivos).encode()).hexdigest()

def generar_indice_sumy():
    os.makedirs("data", exist_ok=True)

    # Verifica si ya existe y si los archivos han cambiado
    nuevo_hash = calcular_hash_archivos(CARPETA_JSONS)
    if os.path.exists(HASH_PATH):
        with open(HASH_PATH, "r") as f:
            antiguo_hash = json.load(f).get("hash")
            if antiguo_hash == nuevo_hash:
                print("✅ El índice ya está actualizado. No se requiere regenerar.")
                return

    # Generar nuevo índice
    indice = []
    for file in os.listdir(CARPETA_JSONS):
        if not file.endswith(".json"):
            continue
        ruta = os.path.join(CARPETA_JSONS, file)
        try:
            with open(ruta, encoding="utf-8") as f:
                contenido = json.load(f)
        except Exception:
            continue

        claves = []
        for clave, valor in contenido.items():
            texto = valor if isinstance(valor, str) else json.dumps(valor)
            try:
                resumen = resumen_sumy(texto)
            except:
                resumen = texto[:200]
            claves.append({
                "ruta": [clave],
                "descripcion": resumen
            })

        indice.append({
            "documento": file,
            "claves": claves
        })

    # Guardar índice y hash
    with open(INDICE_PATH, "w", encoding="utf-8") as f:
        json.dump(indice, f, ensure_ascii=False, indent=2)

    with open(HASH_PATH, "w", encoding="utf-8") as f:
        json.dump({"hash": nuevo_hash}, f)

    print("✅ Índice generado y guardado en 'data/indice_docs.json'")

# Solo se ejecuta si se corre directamente
if __name__ == "__main__":
    generar_indice_sumy()
