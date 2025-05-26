import pandas as pd
from sheets import cargar_hoja

def explicar_ratio_diario(codsalon: str, fecha: str) -> str:
    try:
        df = cargar_hoja("1882861530")
        df = df[df["codsalon"] == int(codsalon)]
        if df.empty:
            return f"⚠️ No se encontraron datos para el salón {codsalon}."

        columnas_necesarias = [
            "fecha", "ratiogeneral", "facturacionsiva", "horasfichadas",
            "ratiodesviaciontiempoteorico", "ratiotiempoindirecto",
            "ratioticketsinferior20", "ticketsivamedio"
        ]
        if not all(col in df.columns for col in columnas_necesarias):
            return "⚠️ Faltan columnas necesarias en los datos."

        fila = df[df["fecha"] == fecha]
        if fila.empty:
            return f"⚠️ No se encontraron datos para la fecha {fecha} en el salón {codsalon}."

        fila = fila.iloc[0]
        ratio = round(float(fila["ratiogeneral"]) * 100)
        explicacion = [f"El Ratio General fue {ratio}% el día {fecha}."]

        # Umbrales razonables para evaluar desviaciones
        umbrales = {
            "ratiotiempoindirecto": 0.25,
            "ratiodesviaciontiempoteorico": 0.2,
            "ratioticketsinferior20": 0.4,
            "horasfichadas": 8,
            "ticketsivamedio": 20,
        }

        if fila["ratiotiempoindirecto"] > umbrales["ratiotiempoindirecto"]:
            explicacion.append("🔸 El tiempo indirecto fue elevado.")

        if fila["ratiodesviaciontiempoteorico"] > umbrales["ratiodesviaciontiempoteorico"]:
            explicacion.append("🔸 Alta desviación del tiempo previsto en la agenda, lo que puede indicar mayor dedicacion de tiempo al cliente del que refleja su ticket.")

        if fila["ratioticketsinferior20"] > umbrales["ratioticketsinferior20"]:
            explicacion.append("🔸 Muchos tickets fueron inferiores a 20 €, recuerda estos ticket dificilmente el ratio objetivo.")

        if fila["ticketsivamedio"] < umbrales["ticketsivamedio"]:
            explicacion.append("🔸 El ticket medio fue bajo, afectando negativamente al ratio.")

        if fila["horasfichadas"] > umbrales["horasfichadas"]:
            explicacion.append("🔸 Se ficharon muchas horas, lo que puede haber incrementado los costes operativos.")

        return "\n".join(explicacion)

    except Exception as e:
        return f"⚠️ Error al procesar los datos: {str(e)}"
