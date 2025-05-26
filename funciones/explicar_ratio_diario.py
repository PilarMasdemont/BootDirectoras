import pandas as pd
from sheets import cargar_hoja

def explicar_ratio_diario(codsalon: str, fecha: str) -> str:
    try:
        df = cargar_hoja("1882861530")
        df = df[df["codsalon"] == int(codsalon)]
        if df.empty:
            return f"No se encontraron datos para el salón {codsalon}."

        df["fecha"] = pd.to_datetime(df["fecha"]).dt.date
        fecha = pd.to_datetime(fecha).date()

        fila = df[df["fecha"] == fecha]
        if fila.empty:
            return f"No hay datos disponibles para la fecha {fecha} en el salón {codsalon}."

        fila = fila.iloc[0]

        intercepto = 1.7034
        pesos = {
            "facturacionsiva": 0.000456213,
            "horasfichadas": -0.012898946,
            "ratiodesviaciontiempoteorico": -1.365456474,
            "ratiotiempoindirecto": -1.897589684,
            "ratioticketsinferior20": -0.103354958,
            "ticketsivamedio": 0.015937312
        }

        causas = {
            "facturacionsiva": "facturación destacada",
            "horasfichadas": "exceso de horas fichadas",
            "ratiodesviaciontiempoteorico": "desviación en la planificación del tiempo",
            "ratiotiempoindirecto": "tiempo indirecto elevado",
            "ratioticketsinferior20": "muchos tickets de importe bajo",
            "ticketsivamedio": "ticket medio alto"
        }

        ratio_real = float(fila["ratiogeneral"])
        ratio_estimado = intercepto
        contribuciones = {}

        for var, peso in pesos.items():
            valor = fila[var]
            contrib = peso * valor
            contribuciones[var] = contrib
            ratio_estimado += contrib

        delta = ratio_real - ratio_estimado
        ratio_pct = round(ratio_real * 100)
        ratio_esp_pct = round(ratio_estimado * 100)

        mensaje = [f"📊 El Ratio General fue {ratio_pct}% el día {fecha}."]

        if abs(delta) < 0.1:
            mensaje.append("Este valor fue similar al esperado según el modelo.")
        elif delta > 0.1:
            mensaje.append(f"Este valor fue más alto de lo esperado ({ratio_esp_pct}%).")
        else:
            mensaje.append(f"Este valor fue más bajo de lo esperado ({ratio_esp_pct}%).")

        positivos = sorted({k: v for k, v in contribuciones.items() if v > 0}.items(), key=lambda x: -x[1])
        negativos = sorted({k: v for k, v in contribuciones.items() if v < 0}.items(), key=lambda x: x[1])

        if delta >= 0:
            if positivos:
                mensaje.append("✅ Factores que contribuyeron positivamente:")
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

        return "\n".join(mensaje)

    except Exception as e:
        return f"❌ Error al analizar el Ratio General: {str(e)}"
