
def explicar_ratio_semanal(datos_semana):
    causas = {
        "facturacionsiva": "facturación destacada",
        "horasfichadas": "exceso de horas fichadas",
        "ratiodesviaciontiempoteorico": "desviación en la planificación del tiempo",
        "ratiotiempoindirecto": "tiempo indirecto elevado",
        "ticketsivamedio": "ticket medio alto",
    }

    coeficientes = {
        "facturacionsiva": 8.87484e-05,
        "horasfichadas": -0.00271686,
        "ratiodesviaciontiempoteorico": -0.9967235,
        "ratiotiempoindirecto": -1.498131,
        "ticketsivamedio": 0.014938,
    }

    intercepto = 1.6347
    real = datos_semana.get("ratiogeneral", 0)
    esperado = intercepto + sum(datos_semana[k] * coeficientes[k] for k in coeficientes)
    delta = round((real - esperado) * 100)

    positivos = []
    negativos = []

    for k, v in coeficientes.items():
        impacto = v * datos_semana.get(k, 0)
        if impacto > 0:
            positivos.append((k, impacto))
        elif impacto < 0:
            negativos.append((k, impacto))

    positivos.sort(key=lambda x: abs(x[1]), reverse=True)
    negativos.sort(key=lambda x: abs(x[1]), reverse=True)

    mensaje = []
    mensaje.append(f"📊 El Ratio General fue {round(real * 100)}% durante la semana.")
    mensaje.append("El resultado estuvo condicionado por varios factores:")

    if delta >= 0:
        if positivos:
            mensaje.append("✅ Factores que ayudaron a mejorar el resultado:")
            for k, v in positivos:
                impacto = round(v * 100)
                mensaje.append(f"  ✅ {causas[k]} (+{impacto}%)")
        if negativos:
            mensaje.append("⚠️ Factores que redujeron el rendimiento:")
            for k, v in negativos:
                impacto = round(v * 100)
                mensaje.append(f"  🔻 {causas[k]} ({impacto}%)")
    else:
        if negativos:
            mensaje.append("⚠️ Factores que redujeron el rendimiento:")
            for k, v in negativos:
                impacto = round(v * 100)
                mensaje.append(f"  🔻 {causas[k]} ({impacto}%)")
        if positivos:
            mensaje.append("✅ Factores que ayudaron a mejorar el resultado:")
            for k, v in positivos:
                impacto = round(v * 100)
                mensaje.append(f"  ✅ {causas[k]} (+{impacto}%)")

    # Sugerencia
    factor_mas_relevante = max(positivos + negativos, key=lambda x: abs(x[1]), default=None)
    if factor_mas_relevante:
        clave, _ = factor_mas_relevante
        if clave in causas:
            mensaje.append(f"💡 Sugerencia: Revisar {causas[clave]}, que fue el factor que más influyó esta semana.")

    return "\n".join(mensaje)

