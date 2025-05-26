import pandas as pd
from sheets import cargar_hoja

def explicar_ratio_empleados(codsalon: str, fecha: str) -> str:
    try:
        df = cargar_hoja("526988839")
        df = df[df["codsalon"] == int(codsalon)]
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.date
        fecha = pd.to_datetime(fecha).date()
        df = df[df["fecha"] == fecha]

        if df.empty:
            return f"No se encontraron datos para el salón {codsalon} en la fecha {fecha}."

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

        mensajes = [f"📆 Explicación de ratios individuales para el {fecha}:\n"]

        for _, fila in df.iterrows():
            nombre = fila["Nombre"]
            ratio_real = float(fila["%RatioGeneral"].split("%")[0]) / 100

            ratio_estimado = intercepto
            contribuciones = {}

            for var, peso in pesos.items():
                valor = fila.get(var, 0)
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
                    mensaje.append(f"  - {causas[k]} (+{round(v*100)}%)")
                if negativos:
                    mensaje.append("⚠️ Algunos factores bajaron el rendimiento:")
                    for k, v in negativos:
                        mensaje.append(f"  - {causas[k]} ({round(v*100)}%)")
            elif delta < 0:
                mensaje.append("🔻 El resultado estuvo penalizado por:")
                for k, v in negativos:
                    mensaje.append(f"  - {causas[k]} ({round(v*100)}%)")
                if positivos:
                    mensaje.append("✅ Aunque hubo elementos positivos como:")
                    for k, v in positivos:
                        mensaje.append(f"  - {causas[k]} (+{round(v*100)}%)")

            if negativos:
                peor = min(negativos, key=lambda x: x[1])
                mensaje.append(f"💡 Sugerencia: Revisar **{causas[peor[0]]}** como posible área de mejora.")

            mensajes.append("\n".join(mensaje))

        return "\n\n".join(mensajes)

    except Exception as e:
        return f"❌ Error al analizar los ratios individuales: {str(e)}"
