from sheets import cargar_hoja

def explicar_ratio_semanal(codsalon: str, nsemana: int) -> str:
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

    try:
        df = cargar_hoja("1579318376")
        df = df[(df["codsalon"] == int(codsalon)) & (df["nsemana"] == int(nsemana))]
        if df.empty:
            return f"⚠️ No se encontraron datos para el salón {codsalon} en la semana {nsemana}."

        fila = df.iloc[0]
        ratio_real = float(fila["ratiogeneral"])
        ratio_estimado = intercepto + sum(fila[k] * coef for k, coef in coeficientes.items())

        delta = ratio_real - ratio_estimado
        ratio_pct = round(ratio_real * 100)

        mensaje = [f"📊 El Ratio General fue {ratio_pct}% durante la semana {nsemana}."]

        positivos = []
        negativos = []

        for k, coef in coeficientes.items():
            impacto = coef * fila[k]
            if impacto > 0:
                positivos.append((k, impacto))
            elif impacto < 0:
                negativos.append((k, impacto))

        positivos.sort(key=lambda x: abs(x[1]), reverse=True)
        negativos.sort(key=lambda x: abs(x[1]), reverse=True)

        if delta >= 0:
            if positivos:
                mensaje.append("✅ Factores que ayudaron a mejorar el resultado:\n")
                for k, v in positivos:
                    mensaje.append(f"  ✅ {causas[k]} (+{round(v * 100)}%)")
            if negativos:
                mensaje.append("⚠️ Factores que redujeron el rendimiento:\n")
                for k, v in negativos:
                    mensaje.append(f"  🔻 {causas[k]} ({round(v * 100)}%)")
        else:
            if negativos:
                mensaje.append("⚠️ Factores que redujeron el rendimiento:\n")
                for k, v in negatives:
                    mensaje.append(f"  🔻 {causas[k]} ({round(v * 100)}%)")
            if positivos:
                mensaje.append("✅ Factores que ayudaron a mejorar el resultado:\n")
                for k, v in positivos:
                    mensaje.append(f"  ✅ {causas[k]} (+{round(v * 100)}%)")

        if negativos:
            clave_peor = min(negativos, key=lambda x: x[1])[0]
            mensaje.append(f"💡 Sugerencia: Revisar {causas[clave_peor]}, que fue el factor que más penalizó el ratio.")

        return "\n".join(mensaje)

    except Exception as e:
        return f"❌ Error al analizar el Ratio General semanal: {str(e)}"
