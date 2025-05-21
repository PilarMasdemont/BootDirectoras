
from funciones.utils import formatear_porcentaje
from sheets import cargar_hoja
import pandas as pd

def explicar_ratio_diario(codsalon: str, fecha: str) -> str:
    df = cargar_hoja("KPIs_30Dias")

    # Conversión robusta de columnas
    df['fecha'] = pd.to_datetime(df['fecha']).dt.date
    fecha_dt = pd.to_datetime(fecha).date()
    df['codsalon'] = df['codsalon'].astype(str)

    fila = df[(df['codsalon'] == str(codsalon)) & (df['fecha'] == fecha_dt)]

    if fila.empty:
        return f"Soy Mont Dirección. No hay registros disponibles para el salón {codsalon} en la fecha {fecha}. Por favor, revisa si hay datos registrados ese día."

    fila = fila.iloc[0]

    # KPIs
    ratiogeneral = fila['ratiogeneral'] * 100
    facturacion = fila['facturacionsiva']
    horas = fila['horasfichadas']
    desviacion = fila['ratiodesviaciontiempoteorico'] * 100
    tiempo_indirecto = fila['ratiotiempoindirecto'] * 100
    ratio_tickets = fila['ratioticketsinferior20'] * 100
    ticket_medio = fila['ticketsivamedio']

    explicacion = f"¡Hola! Soy Mont Dirección. Vamos a analizar el desempeño del salón {codsalon} el día {fecha}.

"
    explicacion += f"📊 El Ratio General fue del {formatear_porcentaje(ratiogeneral)}.
"

    if ratiogeneral < 160:
        explicacion += "Este valor se considera bajo. Vamos a ver por qué:
"
    elif ratiogeneral < 200:
        explicacion += "Este valor se considera aceptable. Veamos qué lo ha influido:
"
    else:
        explicacion += "Este valor se considera excelente. Analicemos las razones:
"

    observaciones = []

    if facturacion > 1000:
        observaciones.append("💰 Alta facturación, lo cual influye positivamente en el rendimiento.")
    if horas > 28:
        observaciones.append("⏱️ Muchas horas fichadas, lo que tiende a reducir la eficiencia si no está bien aprovechado.")
    if desviacion < -5:
        observaciones.append("📅 Alta desviación negativa de la agenda, puede indicar cancelaciones o mal aprovechamiento del tiempo.")
    elif desviacion > 5:
        observaciones.append("📅 Desviación positiva de agenda, se ha superado lo previsto en la planificación.")
    if tiempo_indirecto > 10:
        observaciones.append("🧍‍♂️ Tiempo indirecto elevado, afecta negativamente a la productividad.")
    if ratio_tickets > 20:
        observaciones.append("🎟️ Muchos tickets por debajo de 20€, lo que reduce el valor medio de cada visita.")
    if ticket_medio > 35:
        observaciones.append("💳 Ticket medio alto, un indicador muy positivo para la rentabilidad.")

    if observaciones:
        explicacion += "\n".join(observaciones)
    else:
        explicacion += "No se detectan desviaciones destacadas en los KPIs clave."

    return explicacion
