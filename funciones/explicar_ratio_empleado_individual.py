import pandas as pd


def explicar_ratio_empleado_individual(codsalon: str, fecha: str, codempleado: str) -> str:
    try:
        df = cargar_hoja("526988839")
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        df = df[
            (df["codsalon"] == int(codsalon)) &
            (df["codempleado"] == int(codempleado))
        ]
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.date
        fecha = pd.to_datetime(fecha).date()
        df = df[df["fecha"] == fecha]

        if df.empty:
            return f"No se encontraron datos para el empleado {codempleado} en el salón {codsalon} en la fecha {fecha}."

        fila = df.iloc[0]
        nombre = fila["nombre_empleado"]
        ratio_real = float(str(fila["ratiogeneral"]).replace(",", "."))

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

        ratio_estimado = intercepto
        contribuciones = {}
        for var, peso in pesos.items():
            valor_raw = fila.get(var, 0)
            try:
                valor = float(str(valor_raw).replace(",", "."))
            except:
                valor = 0
            contrib = peso * valor
            contribuciones[var] = contrib
            ratio_estimado += contrib

        delta = ratio_real - ratio_estimado
        ratio_pct = round(ratio_real * 100)
        positivos = sorted([(k, v) for k, v in contribuciones.items() if v > 0], key=lambda x: -x[1])
        negativos = sorted([(k, v) for k, v in contribuciones.items() if v < 0], key=lambda x: x[1])

        mensaje = [f"👤 **{nombre}** - Ratio: {ratio_pct}%"]

        if delta >= 0 and positivos:
            mensaje.append("✅ El resultado se logró gracias a factores clave como:")
            for k, v in positivos:
                mensaje.append(f"  - {causas.get(k, k)} (+{round(v*100)}%)")
            if negativos:
                mensaje.append("⚠️ Algunos factores bajaron el rendimiento:")
                for k, v in negativos:
                    mensaje.append(f"  - {causas.get(k, k)} ({round(v*100)}%)")
        elif delta < 0:
            mensaje.append("🔻 El resultado estuvo penalizado por:")
            for k, v in negativos:
                mensaje.append(f"  - {causas.get(k, k)} ({round(v*100)}%)")
            if positivos:
                mensaje.append("✅ Aunque hubo elementos positivos como:")
                for k, v in positivos:
                    mensaje.append(f"  - {causas.get(k, k)} (+{round(v*100)}%)")

        if negativos:
            peor = min(negativos, key=lambda x: x[1])
            mensaje.append(f"💡 Sugerencia: Revisar **{causas.get(peor[0], peor[0])}** como posible área de mejora.")

        return "\n".join(mensaje)

    except Exception as e:
        return f"❌ Error al analizar el ratio del empleado: {str(e)}"
