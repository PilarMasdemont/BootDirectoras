from extractores import extraer_codempleado, extraer_codsalon, extraer_fecha_desde_texto, detectar_kpi
from extractores_producto import extraer_nombre_producto
from funciones.consultar_proceso import consultar_proceso
from funciones.intencion_total import clasificar_intencion_completa
from funciones.extractores_proceso import extraer_nombre_proceso, extraer_duda_proceso
import re
import logging

logging.basicConfig(level=logging.INFO)

# Diccionario para mantener el contexto por salón
estado_usuarios = {}

def manejar_peticion_chat(datos: dict) -> dict:
    mensaje_usuario = datos.get("mensaje", "")
    codsalon = datos.get("codsalon")
    logging.info(f"📥 Petición recibida: '{mensaje_usuario}'")

    # Paso 1: Clasificar la intención
    datos_intencion = clasificar_intencion_completa(mensaje_usuario)
    intencion = datos_intencion.get("intencion", "general")
    logging.info(f"[INTENCION] Detectada: {intencion} | Datos: {datos_intencion}")

    # Paso 2: Extraer parámetros básicos
    codempleado = extraer_codempleado(mensaje_usuario) if intencion == "empleado" else None
    texto_limpio = re.sub(r"emplead[oa]\s*\d+", "", mensaje_usuario).strip() if codempleado else mensaje_usuario
    fecha = extraer_fecha_desde_texto(texto_limpio)
    codsalon = codsalon or extraer_codsalon(mensaje_usuario)
    kpi = detectar_kpi(mensaje_usuario)

    # Paso 3: Contexto
    contexto = {
        "intencion": intencion,
        "fecha": fecha,
        "codempleado": codempleado,
        "kpi": kpi
    }

    estado_usuarios[codsalon] = contexto  # ⬅️ Guarda contexto por salón

    # ✅ Nueva lógica: resolver seguimiento para proceso
    if intencion == "consultar_proceso":
        nombre_proceso = extraer_nombre_proceso(mensaje_usuario)
        atributo_dudado = extraer_duda_proceso(mensaje_usuario)

        if not nombre_proceso:
            # Intentar recuperar de contexto anterior
            contexto_anterior = estado_usuarios.get(codsalon, {})
            if contexto_anterior.get("intencion") == "consultar_proceso":
                nombre_proceso = contexto_anterior.get("nombre_proceso")

        # Actualizar el contexto con nombre de proceso si se extrajo
        contexto["nombre_proceso"] = nombre_proceso

        respuesta = consultar_proceso(nombre_proceso, atributo_dudado)
        return {
            "intencion": intencion,
            "respuesta": respuesta,
            "codsalon": codsalon,
            "fecha": fecha,
            "codempleado": codempleado
        }

    # Paso 4: Otros resultados
    resultado = {
        "intencion": intencion,
        "tiene_fecha": datos_intencion.get("tiene_fecha", False),
        "codempleado": codempleado,
        "fecha": fecha,
        "codsalon": codsalon,
        "kpi": kpi
    }

    if intencion == "explicar_producto":
        resultado["nombre_producto"] = extraer_nombre_producto(mensaje_usuario)

    return resultado







