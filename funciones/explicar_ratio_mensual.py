import requests

def explicar_ratio_mensual(codsalon: str, mes: int, codempleado: int) -> str:
    causas = {
        "facturacionsiva": "facturación",
        "horasfichadas": "exceso de horas fichadas",
        "ratiodesviaciontiempoteorico": "desviación en la planificación del tiempo",
        "ratiotiempoindirecto": "tiempo indirecto elevado",
        "ratioticketsinferior20": "muchos tickets de importe bajo",
        "n_ticketsiva": "número de tickets",
        "ticketsivamedio": "ticket medio alto",
    }

    coef = {
        "facturacionsiva": -0.000135794,
        "horasfichadas": -0.010839812,
        "ratiodesviaciontiempoteorico": -0.282636521,
        "ratiotiempoindirecto": -0.772379074,
        "ratioticketsinferior20": -1.159725965,
        "n_ticketsiva": 0.01490913,
        "ticketsivamedio": 0.012768938,
    }

    intercepto = 1.5705

    try:
        url = f"https://bootdirectoras.onrender.com/kpis/mensual?codsalon={codsalon}"
        res = requests.get(url)
        if res.status_code != 200:
            return f"❌ Error al obtener datos del servidor: {res.status_code}"

        data = res.json()
        fila = next(
            (d for d in data if int(d["mes"]) == mes and int(d["codempleado"]) == codempleado), None
        )
        if not fila:
            return f"⚠️ No se encontraron datos para el empleado {codempleado} en el mes {mes} del salón {codsalon}."

        real = float(fila["ratiogeneral"])
        estimado = intercepto + sum(float(fila[k]) * v for k, v in coef.items())
        delta = real - estimado

        mensaje = [f"📅 Informe mensual para el empleado {codempleado} (mes {mes}) en el salón {codsalon}."]
        mensaje.append(f"📊 El Ratio General fue {round(real * 100)}%.")

        impactos = [(k, coef[k] * float(fila[k])) for k in coef]
        positivos = sorted([x for x in impactos if x[1] > 0], key=lambda x: abs(x[1]), reverse=True)
        negativos = sorted([x for x in impactos if x[1] < 0], key=lambda x: abs(x[1]), reverse=True)

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
            clave = min(negativos, key=lambda x: x[1])[0]
            mensaje.append(f"💡 Sugerencia: Revisar {causas[clave]}, que fue el factor que más penalizó el ratio.")

        return "\n".join(mensaje)

    except Exception as e:
        return f"❌ Error al analizar el Ratio General mensual: {str(e)}"
