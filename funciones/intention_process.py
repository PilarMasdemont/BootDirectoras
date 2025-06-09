import re
import logging

logger = logging.getLogger(__name__)

def clasificar_intencion(texto: str) -> dict:
    texto = texto.lower().strip()

    # Palabras clave que indican una duda sobre el contenido de un proceso
    patrones_duda_proceso = [
        r"duración", r"cuánto tarda", r"quién lo hace", r"responsable",
        r"cómo se hace", r"instrucciones", r"qué se necesita", r"materiales",
        r"pasos", r"orden", r"funciona", r"flujo", r"procedimiento"
    ]

    # Palabras clave que coinciden con nombres típicos de procesos
    nombres_procesos = [
        "queratina", "mechas", "agenda", "turnos", "inventario",
        "tratamiento", "clientes", "satisfacción", "citas", "caja", "pedidos", "manual"
    ]

    # Si el mensaje contiene dudas comunes sobre un proceso
    if any(re.search(patron, texto) for patron in patrones_duda_proceso):
        return {
            "intencion": "consultar_proceso",
            "comentario": "Consulta sobre aspecto específico de un proceso"
        }

    # Si el mensaje menciona directamente procesos conocidos
    if any(nombre in texto for nombre in nombres_procesos):
        return {
            "intencion": "consultar_proceso",
            "comentario": "Mención directa de un proceso conocido"
        }

    return {
        "intencion": "desconocida",
        "comentario": "No se detecta intención clara sobre procesos"
    }
