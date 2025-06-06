
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
        return "Necesito que me indiques el código de salón para poder analizar el ratio."
    from intenciones.explicar_ratio.ratio_diario import explicar_ratio_diario
    return explicar_ratio_diario(codsalon, fecha, None)



    logging.warning(f"[DISPATCHER] Intención no gestionada directamente: {intencion}")
    return None
