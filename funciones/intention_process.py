import re
import logging

logger = logging.getLogger(__name__)

def clasificar_intencion(texto: str) -> dict:
    texto = texto.lower().strip()

    # 1. Patrones de duda directa sobre un aspecto del proceso
    patrones_duda_proceso = [
        r"duración", r"cuánto dura", r"cuánto tarda", r"tiempo",
        r"quién lo hace", r"responsable", r"encargad[oa]",
        r"cómo se hace", r"cómo va", r"instrucciones", r"qué se necesita",
        r"materiales", r"herramientas", r"pasos", r"orden",
        r"funciona", r"flujo", r"procedimiento", r"explicación", r"manual"
    ]

    # 2. Lista de procesos conocidos que podrían mencionarse
    nombres_procesos = [
        "queratina", "mechas", "agenda", "turnos", "inventario",
        "tratamiento", "clientes", "satisfacción", "citas", "caja", 
        "cerrar caja", "pedidos", "manual", "lavado", "asesoramiento",
        "cerrar día", "apertura", "productos", "stock", "color", 
        "organización", "bienvenida", "revisión"
    ]

    # 3. Frases comunes indicadoras de proceso
    frases_genericas = [
        r"dime el proceso", r"cómo es el proceso", r"explícame el proceso",
        r"cuál es el procedimiento", r"quiero saber el proceso", r"proceso de",
        r"cómo se gestiona", r"gestión de", r"explica el flujo", r"cuáles son los pasos",
        r"manual de", r"rutina de", r"cómo hacemos"
    ]

    # 🔍 Verificación por patrones específicos
    if any(re.search(patron, texto) for patron in patrones_duda_proceso):
        return {
            "intencion": "consultar_proceso",
            "comentario": "Consulta sobre aspecto específico de un proceso"
        }

    # 🔍 Verificación por frases comunes de consulta de procesos
    if any(re.search(patron, texto) for patron in frases_genericas):
        return {
            "intencion": "consultar_proceso",
            "comentario": "Frase típica que solicita proceso completo"
        }

    # 🔍 Verificación por mención directa de nombres de procesos
    if any(nombre in texto for nombre in nombres_procesos):
        return {
            "intencion": "consultar_proceso",
            "comentario": "Mención directa de un proceso conocido"
        }

    # ❌ Nada detectado
    return {
        "intencion": "desconocida",
        "comentario": "No se detecta intención clara sobre procesos"
    }

