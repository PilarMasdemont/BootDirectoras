from funciones.utils import formatear_porcentaje
from sheets import cargar_hoja
from datetime import datetime

def explicar_ratio_diario(codsalon: str, fecha: str) -> str:
    df = cargar_hoja("KPIs_30Dias")
    df['fecha'] = df['fecha'].astype(str)

    # 🧠 Extraer día y mes de la fecha solicitada
    try:
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
        dia_mes = fecha_obj.strftime("%m-%d")
    except Exception as e:
        return f"⚠️ No pude entender la fecha '{fecha}'. Asegúrate de usar el formato correcto (YYYY-MM-DD)."

    # 🎯 Buscar fechas que coincidan con ese día y mes
    df['dia_mes'] = df['fecha'].str[5:]  # extrae MM-DD
    posibles_fechas = df[df['dia_mes'] == dia_mes]

    # 🔍 Filtrar por código de salón
    posibles_fechas = posibles_fechas[df['codsalon'].astype(str) == str(codsalon)]

    if posibles_fechas.empty:
        return f"Soy Mont Dirección. No encontré registros para el salón {codsalon} el día {fecha}. Revisa si hay datos ese día."

    # 🗓️ Seleccionar la más reciente (por si hay varias coincidencias de año)
    fila = posibles_fechas.sort_values('fecha', ascending=False).iloc[0]

    # 📊 Extraer y convertir métricas
    ratiogeneral = fila['ratiogeneral'] * 100
    facturacion = fila['facturacionsiva']
    horas = fila['horasfichadas']
    desviacion = fila['ratiodesviaciontiempoteorico'] * 100
    tiempo_indirecto = fila['ratiotiempoindirecto'] * 100
    ratio_tickets = fila['ratioticketsinferior20'] * 100
    ticket_medio = fila['ticketsivamedio']

    explicacion = f"¡Hola! Soy Mont Dirección. Vamos a analizar el desempeño del salón {codsalon} el día {fila['fecha']}.\n\n"
    explicacion += f"📊 El Ratio General fue del {formatear_porcentaje(ratiogeneral)}.\n"

    observaciones = []

    if ratiogeneral < 160:
        explicacion += "Este valor se considera bajo. Vamos a ver por qué:\n"
    elif ratiogeneral < 200:
        explicacion += "Este valor se considera aceptable. Veamos qué lo ha influido:\n"
    else:
        explicacion += "Este valor se considera excelente. Analicemos las razones:\n"

    if facturacion > 1000:
        observaciones.append("💰 Alta facturación, lo cual influye positivamente en el rendimiento.")
    if horas > 28:
        observaciones.append("⏱️ Muchas horas fichadas, lo que puede reducir la eficiencia si no están bien aprovechadas.")
    if desviacion < -5:
        observaciones.append("📅 Alta desviación negativa de agenda, posible señal de cancelaciones o tiempo mal gestionado.")
    elif desviacion > 5:
        observaciones.append("📅 Desviación positiva, se ha superado lo planeado.")
    if tiempo_indirecto > 10:
        observaciones.append("🧍‍♂️ Tiempo indirecto elevado, afecta negativamente a la productividad.")
    if ratio_tickets > 20:
        observaciones.append("🎟️ Muchos tickets por debajo de 20€, lo que baja el valor promedio por cliente.")
    if ticket_medio > 35:
        observaciones.append("💳 Ticket medio alto, un dato muy positivo para la rentabilidad.")

    if observaciones:
        explicacion += "\n".join(observaciones)
    else:
        explicacion += "No se detectan desviaciones destacadas en los KPIs clave."

    return explicacion

