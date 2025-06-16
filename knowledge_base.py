# knowledge_base.py
import json
import os

RUTA_JSON = os.path.join(os.path.dirname(__file__), "bot_conocimiento_completo_enriquecido.json")

with open(RUTA_JSON, "r", encoding="utf-8") as f:
    base_conocimiento = json.load(f)
