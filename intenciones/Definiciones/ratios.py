import json
import os

def definicion_kpi(nombre_kpi: str) -> str:
    ruta_base = os.path.dirname(__file__)
    ruta_json = os.path.abspath(os.path.join(ruta_base, "../../datosestaticos/definicionratios.json"))
    
    try:
        with open(ruta_json, 'r', encoding='utf-8') as f:
            definiciones = json.load(f)
        
        # Normaliza la clave buscada (sensible a mayúsculas/minúsculas)
        clave = nombre_kpi.replace(" ", "").replace("_", "")
        claves_posibles = {k.lower(): v for k, v in definiciones.items()}
        
        definicion = claves_posibles.get(clave.lower())
        if definicion:
            return definicion
        else:
            return f"No tengo registrada la definición del KPI o ratio '{nombre_kpi}'."
    
    except Exception as e:
        return f"Error al leer las definiciones: {str(e)}"
