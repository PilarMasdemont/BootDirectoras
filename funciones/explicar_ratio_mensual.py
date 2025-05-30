import pandas as pd
from sheets import cargar_hoja

def explicar_ratio_mensual(codsalon: str, mes: int, codempleado: str) -> str:
    try:
        # ID de la hoja mensual
        hoja_id = "1194190690"  # Reemplazar con el ID real si cambia
        df = cargar_hoja(hoja_id)

        # Asegurarse que los tipos son correctos
        df["codsalon"] = df["codsalon"].astype(str)
        df["codempleado"] = df["codempleado"].astype(str)
        df["mes"] = df["mes"].astype(int)

        # Filtrado por parámetros
        datos = df[
            (df["codsalon"] == codsalon) &
            (df["codempleado"] == codempleado) &
            (df["mes"] == mes)
        ]

        if datos.empty:
            return f"No se encontraron datos para el empleado {codempleado} del salón {codsalon} en el mes {mes}."

        fila = datos.iloc[0]

        # Interpretación básica de KPIs
        resumen = []

        if fila["ratiogeneral"] < 1.5:
            resumen.append("El ratio general fue bajo, indicando baja rentabilidad relativa al coste laboral.")
        elif fila["ratiogeneral"] > 2:
            resumen.append("El ratio general fue alto, señal de muy buena rentabilidad.")

        if fila["ratiotiempoindirecto"] > 0.25:
            resumen.append("El tiempo indirecto fue elevado, lo que puede indicar ineficiencias o tiempos no productivos excesivos.")

        if fila["ratiodesviaciontiempoteorico"] < -0.1:
            resumen.append("Se observó una desviación negativa significativa entre el tiempo planificado y el trabajado.")

        if fila["ratioticketsinferior20"] > 0.3:
            resumen.append("Un alto porcentaje de tickets fueron inferiores a 20€, lo que puede afectar la rentabilidad.")

        if fila["facturacionsiva"] < 1000:
            resumen.append("La facturación mensual fue baja.")

        if not resumen:
            resumen.append("Los indicadores clave se mantienen dentro de los valores aceptables para este mes.")

        return f"Análisis mensual del empleado {codempleado} en el salón {codsalon} para el mes {mes}:\n- " + "\n- ".join(resumen)

    except Exception as e:
        return f"Error al procesar la explicación mensual: {str(e)}"
