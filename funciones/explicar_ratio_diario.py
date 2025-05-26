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

        # Coeficientes del modelo
        intercepto = 1.7034
        pesos = {
            "facturacionsiva": 0.000456213,
            "horasfichadas": -0.012898946,
            "ratiodesviaciontiempoteorico": -1.365456474,
            "ratiotiempoindirecto": -1.897589684,
            "ratioticketsinferior20": -0.103354958,
            "ticketsivamedio": 0.015937312
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
        mensaje = [f"El Ratio General fue {ratio_pct}% el día {fecha}."]

        if abs(delta) < 0.1:
            mensaje.append("Este valor fue muy similar a lo que esperábamos según el comportamiento habitual del salón.")
        elif delta > 0.1:
            mensaje.append(f"Este valor fue más alto de lo esperado (esperábamos {ratio_esp_pct}%), lo cual es una buena noticia.")
        else:
            mensaje.append(f"Este valor fue más bajo de lo esperado (esperábamos {ratio_esp_pct}%).")

        # Detectamos factores principales que afectaron el ratio
        factor_principal = max(contribuciones.items(), key=lambda x: abs(x[1]))

        causas = {
            "facturacionsiva": "una buena facturación",
            "horasfichadas": "una alta cantidad de horas fichadas",
            "ratiodesviaciontiempoteorico": "una desviación en la planificación del tiempo",
            "ratiotiempoindirecto": "un tiempo indirecto elevado",
            "ratioticketsinferior20": "muchos tickets de importe bajo",
            "ticketsivamedio": "un ticket medio alto"
        }

        efecto = "positivamente" if factor_principal[1] > 0 else "negativamente"
        mensaje.append(f"El principal factor que afectó el resultado fue {causas[factor_principal[0]]}, que influyó {efecto} en el Ratio General.")

        return "\n".join(mensaje)

    except Exception as e:
        return f"Error al analizar el Ratio General: {str(e)}"
