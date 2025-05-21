
from funciones.utils import formatear_porcentaje
from funciones.sheets import cargar_hoja

def explicar_ratio_diario(codsalon: str, fecha: str) -> str:
    df = cargar_hoja("KPIs_30Dias")
    df['fecha'] = df['fecha'].astype(str)
    fila = df[(df['codsalon'].astype(str) == str(codsalon)) & (df['fecha'] == fecha)]

    if fila.empty:
        return f"Soy Mont Dirección. No hay registros disponibles para el salón {codsalon} en la fecha {fecha}. Por favor, revisa si hay datos registrados ese día."

    fila = fila.iloc[0]

    # Cargar los valores y convertir a porcentajes cuando corresponda
    ratiogeneral = fila['ratiogeneral'] * 100
    facturacion = fila['facturacionsiva']
    horas = fila['horasfichadas']
    desviacion = fila['ratiodesviaciontiempoteorico'] * 100
    tiempo_indirecto = fila['ratiotiempoindirecto'] * 100
    ratio_tickets = fila['ratioticketsinferior20'] * 100
    ticket_medio = fila['ticketsivamedio']

    explicacion = []

    # Clasificación del Ratio General según umbrales del informe
    if ratiogeneral < 160:
        resumen = f"📊 El Ratio General fue del {formatear_porcentaje(ratiogeneral)}, lo cual se considera BAJO."
    elif 160 <= ratiogeneral <= 200:
        resumen = f"📊 El Ratio General fue del {formatear_porcentaje(ratiogeneral)}, lo cual se considera ACEPTABLE."
    else:
        resumen = f"📊 El Ratio General fue del {formatear_porcentaje(ratiogeneral)}, lo cual se considera EXCELENTE."

    # Coeficientes del modelo de regresión lineal
    pesos = {
        'facturacionsiva': 0.000456213,
        'horasfichadas': -0.01289895,
        'ratiodesviaciontiempoteorico': -1.365456474,
        'ratiotiempoindirecto': -1.897589684,
        'ratioticketsinferior20': -0.103354958,
        'ticketsivamedio': 0.015937312
    }

    # Construir el diccionario con los valores normalizados
    valores = {
        'facturacionsiva': facturacion,
        'horasfichadas': horas,
        'ratiodesviaciontiempoteorico': desviacion,
        'ratiotiempoindirecto': tiempo_indirecto,
        'ratioticketsinferior20': ratio_tickets,
        'ticketsivamedio': ticket_medio
    }

    impacto = {}
    for kpi, coef in pesos.items():
        impacto[kpi] = coef * valores[kpi]

    causas_negativas = sorted(impacto.items(), key=lambda x: x[1])[:3]

    for kpi, valor in causas_negativas:
        if valor < -0.1:
            if kpi == 'ratiodesviaciontiempoteorico':
                explicacion.append("📅 Hubo una desviación significativa respecto al tiempo teórico previsto en agenda.")
            elif kpi == 'ratiotiempoindirecto':
                explicacion.append("🧍‍♂️ Se dedicó un tiempo elevado a tareas no productivas o indirectas.")
            elif kpi == 'ratioticketsinferior20':
                explicacion.append("🎟️ Muchos tickets fueron de menos de 20€, reduciendo la rentabilidad.")
            elif kpi == 'horasfichadas':
                explicacion.append("⏱️ Se ficharon muchas horas en relación con los ingresos obtenidos.")
            elif kpi == 'facturacionsiva':
                explicacion.append("💰 La facturación fue baja en comparación con otras jornadas.")
            elif kpi == 'ticketsivamedio':
                explicacion.append("💳 El ticket medio fue más bajo de lo habitual.")

    if not explicacion:
        explicacion.append("✅ No se detectan desviaciones relevantes en los KPIs clave para ese día.")

    return f"¡Hola! Soy Mont Dirección. Vamos a analizar el desempeño del salón {codsalon} el día {fecha}."

" + resumen + "

" + "
".join(explicacion)
