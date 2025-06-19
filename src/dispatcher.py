import logging

def despachar_intencion(
    intencion: str,
    texto_usuario: str,
    fecha=None,
    codsalon=None,
    codempleado=None,
    kpi=None,
    sesion=None
):
    logging.info(f"[DISPATCHER] Intenci\u00f3n recibida: {intencion}")

    if intencion == "ratio_empleado":
        from intenciones.explicar_ratio.ratio_empleado import explicar_ratio_empleado_individual
        return explicar_ratio_empleado_individual(codsalon, fecha, codempleado)

    elif intencion == "ratio_dia":
        from intenciones.explicar_ratio.ratio_diario import explicar_ratio_diario
        return explicar_ratio_diario(codsalon, fecha, kpi)

    elif intencion == "general":
        if not codsalon:
            logging.warning("[DISPATCHER] codsalon es None — no se puede continuar")
            return "Necesito que me indiques el c\u00f3digo de sal\u00f3n para poder analizar el ratio."
        from intenciones.explicar_ratio.ratio_diario import explicar_ratio_diario
        return explicar_ratio_diario(codsalon, fecha, None)

    elif intencion == "empleado":
        if not codsalon or not codempleado:
            logging.warning("[DISPATCHER] Falta codsalon o codempleado para intenci\u00f3n 'empleado'")
            return "Necesito el c\u00f3digo de sal\u00f3n y del empleado para responderte correctamente."
        from intenciones.explicar_ratio.ratio_empleado import explicar_ratio_empleado_individual
        return explicar_ratio_empleado_individual(codsalon, fecha, codempleado)

    elif intencion == "consultar_proceso":
        logging.info("[DISPATCHER] Ejecutando flujo de proceso")
        from funciones.consultar_proceso_con_chatgpt import consultar_proceso_chatgpt as consultar_proceso
        from funciones.extractores_proceso import extraer_nombre_proceso, extraer_duda_proceso

        nombre_proceso = extraer_nombre_proceso(texto_usuario)
        atributo_duda = extraer_duda_proceso(texto_usuario)

        logging.info(f"[PROCESO] Nombre detectado: {nombre_proceso}")
        logging.info(f"[PROCESO] Atributo detectado: {atributo_duda}")

        if not nombre_proceso:
            return "No pude identificar el proceso al que te refieres."
        if not atributo_duda:
            return f"¿Qué parte del proceso '{nombre_proceso}' quieres consultar? (por ejemplo: duración, pasos...)"

        return consultar_proceso(nombre_proceso, atributo_duda)

    elif intencion == "consultar_producto":
        logging.info("[DISPATCHER] Ejecutando flujo de producto")
        from funciones.consultar_producto_con_chatgpt import consultar_producto_chatgpt as consultar_producto
        from funciones.extractores_producto import extraer_nombre_producto, extraer_duda_producto

        nombre_producto = extraer_nombre_producto(texto_usuario)
        atributo_duda = extraer_duda_producto(texto_usuario)

        logging.info(f"[PRODUCTO] Nombre detectado: {nombre_producto}")
        logging.info(f"[PRODUCTO] Atributo detectado: {atributo_duda}")

        if not nombre_producto:
            return "No pude identificar el producto al que te refieres."
        if not atributo_duda:
            return f"¿Qué parte del producto '{nombre_producto}' quieres consultar? (por ejemplo: uso, beneficio, ingredientes...)"

        return consultar_producto(nombre_producto, atributo_duda)

    logging.warning(f"[DISPATCHER] Intención no gestionada directamente: {intencion}")
    return None




