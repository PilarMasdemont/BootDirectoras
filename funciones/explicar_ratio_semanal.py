import requests

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
        res = requests.get(f"https://bootdirectoras.onrender.com/kpis/semanal?codsalon={codsalon}")
        if res.status_code != 200:
            return f"❌ Error al obtener datos del servidor: {res.status_code}"
        data = res.json()
        fila = next((d for d in data if int(d['nsemana']) == int(nsemana)), None)
        if not fila:
            return f"⚠️ No se encontraron datos para la semana {nsemana} en el salón {codsalon}."

        ratio_real = float(fila["ratiogeneral"])
        ratio_estimado = intercepto + sum(float(fila[k]) * coef for k, coef in coeficientes.items())

        delta = ratio_real - ratio_estimado
        ratio_pct = round(ratio_real * 100)

        mensaje = [f"📊 El Ratio General fue {ratio_pct}% durante la semana {nsemana} en el salón {codsalon}."]

        positivos = []
        negativos = []

        for k, coef in coeficientes.items():
            impacto = coef * float(fila[k])
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
                for k, v in negativos:
                    mensaje.append(f"  🔻 {causas[k]} ({round(v * 100)}%)")
            if positivos:
                mensaje.append("✅ Factores que ayudaron a mejorar el resultado:\n")
                for k, v in positivos:
                    mensaje.append(f"  ✅ {causas[k]} (+{round(v * 100)}%)")

        if negativos:
            factor_peor = min(negativos, key=lambda x: x[1])[0]
            mensaje.append(f"💡 Sugerencia: Revisar {causas[factor_peor]}, que fue el factor que más penalizó el ratio.")

        return "\n".join(mensaje)

    except Exception as e:
        return f"❌ Error al analizar el Ratio General semanal: {str(e)}"
