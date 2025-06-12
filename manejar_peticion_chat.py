from extractores import extraer_codempleado, extraer_codsalon, extraer_fecha_desde_texto, detectar_kpi
from extractores_producto import extraer_nombre_producto
import re
import logging
from funciones.intencion_total import clasificar_intencion_completa

logging.basicConfig(level=logging.INFO)

# 🧠 Memoria temporal (clave por codsalon como pseudo-id)
estado_usuarios = {}

def manejar_peticion_chat(datos: dict) -> dict:
    mensaje_usuario = datos.get("mensaje", "")
    codsalon = datos.get("codsalon", "global")  # usamos esto como ID si no hay multiusuario

    logging.info(f"📥 Petición recibida: '{mensaje_usuario}'")

    # Paso 1: Clasificar la intención
    datos_intencion = clasificar_intencion_completa(mensaje_usuario)
    intencion = datos_intencion.get("intencion", "general")
    logging.info(f"[INTENCION] Detectada: {intencion} | Datos: {datos_intencion}")

    # Estado previo
    contexto = estado_usuarios.get(codsalon, {})

    # Paso 2: Manejo de intención parcial
    if intencion == "consultar_proceso":
        # Si no hay proceso pero antes hubo, reutilizar
        if not datos_intencion.get("proceso") and contexto.get("proceso"):
            datos_intencion["proceso"] = contexto["proceso"]
            logging.info(f"[MEMORIA] Usando proceso previo: {contexto['proceso']}")
        # Lo mismo con atributo
        if not datos_intencion.get("atributo") and contexto.get("atributo"):
            datos_intencion["atributo"] = contexto["atributo"]
            logging.info(f"[MEMORIA] Usando atributo previo: {contexto['atributo']}")

        # Actualizar memoria
        if datos_intencion.get("proceso"):
            contexto["proceso"] = datos_intencion["proceso"]
        if datos_intencion.get("atributo"):
            contexto["atributo"] = datos_intencion["atributo"]

        estado_usuarios[codsalon] = contexto

    # Paso 3: Preparar texto según intención
    if intencion == "empleado":
        codempleado = extraer_codempleado(mensaje_usuario)
        logging.info(f"[EXTRACCION] Código de empleado detectado: {codempleado}")
        texto_limpio = re.sub(r"emplead[oa]\\s*\\d+", "", mensaje_usuario)
        texto_limpio = re.sub(r"\\s{2,}", " ", texto_limpio).strip()
    else:
        codempleado = None
        texto_limpio = mensaje_usuario

    logging.info(f"[LIMPIEZA] Texto para extracción de fecha: '{texto_limpio}'")

    fecha = extraer_fecha_desde_texto(texto_limpio)
    logging.info(f"[FECHA] Extraída: {fecha}")

    if not codsalon:
        codsalon = extraer_codsalon(mensaje_usuario)
    logging.info(f"[SALON] Código detectado: {codsalon}")

    kpi = detectar_kpi(mensaje_usuario)
    logging.info(f"[KPI] Detectado: {kpi}")

    resultado = {
        "intencion": intencion,
        "tiene_fecha": datos_intencion.get("tiene_fecha", False),
        "codempleado": codempleado,
        "fecha": fecha,
        "codsalon": codsalon,
        "kpi": kpi,
        "proceso": datos_intencion.get("proceso"),
        "atributo": datos_intencion.get("atributo")
    }

    if intencion == "explicar_producto":
        resultado["nombre_producto"] = extraer_nombre_producto(mensaje_usuario)
        logging.info(f"[PRODUCTO] Detectado: {resultado['nombre_producto']}")

    return resultado





