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
    logging.info(f"[DISPATCHER] Intención recibida: {intencion}")

    if intencion == "ratio_empleado":
        from intenciones.explicar_ratio.ratio_empleado import explicar_ratio_empleado_individual
        return explicar_ratio_empleado_individual(codsalon, fecha, codempleado)

    elif intencion == "ratio_dia":
        from intenciones.explicar_ratio.ratio_diario import explicar_ratio_diario
        return explicar_ratio_diario(codsalon, fecha, kpi)

    elif intencion == "general":
        if not codsalon:
            logging.warning("[DISPATCHER] codsalon es None — no se puede continuar")
            return "Necesito que me indiques el código de salón para poder analizar el ratio."
        from intenciones.explicar_ratio.ratio_diario import explicar_ratio_diario
        return explicar_ratio_diario(codsalon, fecha, None)

    elif intencion == "empleado":
        if not codsalon or not codempleado:
            logging.warning("[DISPATCHER] Falta codsalon o codempleado para intención 'empleado'")
            return "Necesito el código de salón y del empleado para responderte correctamente."
        from intenciones.explicar_ratio.ratio_empleado import explicar_ratio_empleado_individual
        return explicar_ratio_empleado_individual(codsalon, fecha, codempleado)

    elif intencion == "consultar_proceso":
        logging.info("[DISPATCHER] Ejecutando flujo de proceso")
        from funciones.consultar_proceso import consultar_proceso
        from Archivos_estaticos.extractores_proceso import extraer_nombre_proceso, extraer_duda_proceso

        nombre_proceso = extraer_nombre_proceso(texto_usuario)
        atributo_duda = extraer_duda_proceso(texto_usuario)

        logging.info(f"[PROCESO] Nombre detectado: {nombre_proceso}")
        logging.info(f"[PROCESO] Atributo detectado: {atributo_duda}")

        if not nombre_proceso:
            return "No pude identificar el proceso al que te refieres."
        if not atributo_duda:
            return f"¿Qué parte del proceso '{nombre_proceso}' quieres consultar? (por ejemplo: duración, pasos...)"

        return consultar_proceso(nombre_proceso, atributo_duda)

    logging.warning(f"[DISPATCHER] Intención no gestionada directamente: {intencion}")
    return None


