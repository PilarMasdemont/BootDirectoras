# solo se muestra lo modificado respecto al contexto

...

    contexto = obtener_contexto(codsalon)

    # Resetear contexto si cambia la intención
    if intencion != contexto.get("intencion"):
        limpiar_contexto(codsalon)
    actualizar_contexto(codsalon, "intencion", intencion)

    actualizar_contexto(codsalon, "codsalon", codsalon)
    actualizar_contexto(codsalon, "fecha", fecha)
    actualizar_contexto(codsalon, "codempleado", codempleado)
    actualizar_contexto(codsalon, "kpi", kpi)

    resultado = despachar_intencion(
        intencion=intencion,
        texto_usuario=mensaje_usuario,
        fecha=fecha,
        codsalon=codsalon,
        codempleado=codempleado,
        kpi=kpi,
        sesion=contexto
    )
...




