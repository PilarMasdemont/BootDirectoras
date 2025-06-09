import logging

logger = logging.getLogger(__name__)

REQUISITOS = {
    "ratio_dia": ["fecha", "codsalon"],
    "ratio_empleado": ["fecha", "codsalon", "codempleado"],
    "empleado": ["fecha", "codsalon", "codempleado"],
    "general": ["codsalon"],
    "kpi": ["kpi"]
}

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
    logging.info(f"[DISPATCHER] Parámetros recibidos: fecha={fecha}, codsalon={codsalon}, codempleado={codempleado}, kpi={kpi}")

    # Validación de requisitos mínimos según la intención
    faltantes = []
    parametros = {
        "fecha": fecha,
        "codsalon": codsalon,
        "codempleado": codempleado,
        "kpi": kpi
    }
    for campo in REQUISITOS.get(intencion, []):
        if not parametros.get(campo):
            faltantes.append(campo)

    if faltantes:
        logging.info(f"[DISPATCHER] Faltan parámetros requeridos: {faltantes}")
        return f"Necesito que me indiques: {', '.join(faltantes)} para poder responder correctamente."

    if intencion == "ratio_empleado":
        logging.info(f"[DISPATCHER] Despachando a ratio_empleado con codsalon={codsalon}, fecha={fecha}, codempleado={codempleado}")
        from intenciones.explicar_ratio.ratio_empleado import explicar_ratio_empleado_individual
        return explicar_ratio_empleado_individual(codsalon, fecha, codempleado)

    elif intencion == "ratio_dia":
        logging.info(f"[DISPATCHER] Despachando a ratio_dia con codsalon={codsalon}, fecha={fecha}, kpi={kpi}")
        from intenciones.explicar_ratio.ratio_diario import explicar_ratio_diario
        return explicar_ratio_diario(codsalon, fecha, kpi)

    elif intencion == "general":
        if not fecha:
            logging.warning("[DISPATCHER] Falta fecha para intención 'general'")
            return "¿Podrías indicarme la fecha para poder analizar el ratio del día?"
        if not codsalon:
            logging.warning("[DISPATCHER] codsalon es None — no se puede continuar")
            return "Necesito que me indiques el código de salón para poder analizar el ratio."
        logging.info(f"[DISPATCHER] Despachando a general con codsalon={codsalon}, fecha={fecha}")
        from intenciones.explicar_ratio.ratio_diario import explicar_ratio_diario
        return explicar_ratio_diario(codsalon, fecha, None)

    elif intencion == "empleado":
        logging.info(f"[DISPATCHER] Despachando a empleado con codsalon={codsalon}, fecha={fecha}, codempleado={codempleado}")
        from intenciones.explicar_ratio.ratio_empleado import explicar_ratio_empleado_individual
        return explicar_ratio_empleado_individual(codsalon, fecha, codempleado)

    elif intencion == "kpi":
        logging.info(f"[DISPATCHER] Despachando a definición de KPI: {kpi}")
        from intenciones.explicar_kpi import definicion_kpi
        return definicion_kpi(kpi)

    logging.warning(f"[DISPATCHER] Intención no gestionada directamente: {intencion}")
    return None
