
def explicar_ratio_mensual(data, empleado, mes, cod_salon):
    """
    Genera una explicación sobre el Ratio General mensual de un empleado basado en un modelo de regresión lineal.
    """
    from datetime import datetime
    mensaje = []

    # Filtrado
    fila = next((d for d in data if d["empleado"] == empleado and d["mes"] == mes and d["codsalon"] == cod_salon), None)
    if not fila:
        return f"⚠️ No se encontraron datos para el empleado {empleado}, salón {cod_salon} en el mes {mes}."

    # Variables relevantes
    actual = fila["ratiogeneral"]
    predicho = (
        1.5705
        - 0.0001358 * fila["facturacionsiva"]
        - 0.01084 * fila["horasfichadas"]
        - 0.2826 * fila["ratiodesviaciontiempoteorico"]
        - 0.7724 * fila["ratiotiempoindirecto"]
        - 1.1597 * fila["ratioticketsinferior20"]
        + 0.01491 * fila["n_ticketsiva"]
        + 0.01277 * fila["ticketsivamedio"]
    )
    delta = actual - predicho

    mensaje.append(f"📆 Informe mensual para el empleado {empleado} en el mes {mes}.")
    mensaje.append(f"📊 El Ratio General fue {round(actual * 100)}%.")

    # Cálculo de impactos individuales
    factores = {
        "facturacionsiva": -0.0001358,
        "horasfichadas": -0.01084,
        "ratiodesviaciontiempoteorico": -0.2826,
        "ratiotiempoindirecto": -0.7724,
        "ratioticketsinferior20": -1.1597,
        "n_ticketsiva": 0.01491,
        "ticketsivamedio": 0.01277,
    }
    causas = {
        "facturacionsiva": "facturación",
        "horasfichadas": "exceso de horas fichadas",
        "ratiodesviaciontiempoteorico": "desviación en la planificación del tiempo",
        "ratiotiempoindirecto": "tiempo indirecto elevado",
        "ratioticketsinferior20": "muchos tickets de importe bajo",
        "n_ticketsiva": "número de tickets",
        "ticketsivamedio": "ticket medio alto",
    }

    impactos = [(k, factores[k] * fila[k]) for k in factores]
    positivos = [(k, v) for k, v in impactos if v > 0]
    negativos = [(k, v) for k, v in impactos if v < 0]

    if delta >= 0:
        if positivos:
            mensaje.append("✅ Factores que contribuyeron positivamente:")
            for k, v in sorted(positivos, key=lambda x: -x[1]):
                mensaje.append(f"  ✅ {causas[k]} (+{round(v * 100)}%)")
        if negativos:
            mensaje.append("⚠️ Factores que redujeron el rendimiento:")
            for k, v in sorted(negativos, key=lambda x: x[1]):
                mensaje.append(f"  🔻 {causas[k]} ({round(v * 100)}%)")
    else:
        if negativos:
            mensaje.append("⚠️ Factores que redujeron el rendimiento:")
            for k, v in sorted(negativos, key=lambda x: x[1]):
                mensaje.append(f"  🔻 {causas[k]} ({round(v * 100)}%)")
        if positivos:
            mensaje.append("✅ Factores que ayudaron a mejorar el resultado:")
            for k, v in sorted(positivos, key=lambda x: -x[1]):
                mensaje.append(f"  ✅ {causas[k]} (+{round(v * 100)}%)")

    # Sugerencia final
    if negativos:
        factor_principal = sorted(negativos, key=lambda x: x[1])[0][0]
        mensaje.append(f"💡 Sugerencia: Revisar {causas[factor_principal]}, que fue el factor que más penalizó el ratio.")

    return "\n".join(mensaje)
