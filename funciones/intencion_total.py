import re

def clasificar_intencion_completa(texto_usuario: str) -> dict:
    texto = texto_usuario.lower()

    # Intenciones simples
    if "ratio" in texto or "porcentaje" in texto:
        return {"intencion": "consultar_ratio"}
    
    if "inventario" in texto or "stock" in texto:
        return {"intencion": "consultar_proceso", "proceso": "inventario"}
    
    if "caja" in texto and "cerrar" in texto:
        return {"intencion": "consultar_proceso", "proceso": "cierre_caja"}

    if any(p in texto for p in ["queratina", "mechas", "color", "tratamiento", "alisado", "corte"]):
        return {"intencion": "explicar_servicio"}

    if any(p in texto for p in ["masdemont", "método", "metodo"]):
        return {"intencion": "explicar_metodo"}

    # Procesos por defecto
    match_proceso = re.search(r"(cómo|como) (se )?(hace|realiza|funciona) (el|un|una)?\s?([\w\s]+)", texto)
    if match_proceso:
        posible_proceso = match_proceso.group(5).strip()
        return {
            "intencion": "consultar_proceso",
            "proceso": posible_proceso
        }

    return {
        "intencion": "general"
    }


