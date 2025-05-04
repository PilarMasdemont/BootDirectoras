# funciones/kpis.py

def consultar_kpis(year: int, nsemana: int, codsalon: int, tipo: str = "semana") -> str:
    # Simulación de datos por ahora. Luego se conectará a Google Sheets.
    return (
        f"🔍 Datos simulados para el salón {codsalon}, semana {nsemana}, año {year}, tipo '{tipo}'. "
        f"Ingresos: 1.500€, Clientes: 90, Ticket medio: 16,66€."
    )

def explicar_kpi(nombre_kpi: str) -> str:
    explicaciones = {
        "ingresos": "Total de dinero generado por los servicios realizados.",
        "clientes": "Cantidad de personas atendidas durante el periodo.",
        "ticket_medio": "Promedio de gasto por cliente (ingresos / clientes).",
        "ratio_general": "Porcentaje que indica la eficiencia operativa del salón.",
    }
    return explicaciones.get(nombre_kpi.lower(), "No tengo una explicación registrada para ese KPI.")

def analizar_salon(year: int, nsemana: int, codsalon: int) -> str:
    return (
        f"📊 Análisis del salón {codsalon} en la semana {nsemana} de {year}: "
        f"Buen rendimiento en ingresos y visitas. Se recomienda revisar el ticket medio."
    )

def explicar_variacion(kpi: str, valor_actual: float, valor_anterior: float) -> str:
    variacion = valor_actual - valor_anterior
    if variacion > 0:
        tendencia = "aumento"
    elif variacion < 0:
        tendencia = "disminución"
    else:
        tendencia = "sin cambios"
    return f"El KPI '{kpi}' tuvo una {tendencia} de {abs(variacion):.2f} unidades respecto al periodo anterior."

def analizar_trabajadores(year: int, nsemana: int, codsalon: int) -> str:
    return (
        f"👥 Análisis por trabajador para salón {codsalon}, semana {nsemana} de {year}: "
        f"Trabajador A: 45 clientes. Trabajador B: 30 clientes. Trabajador C: 15 clientes."
    )

def sugerencias_mejora(year: int, nsemana: int, codsalon: int) -> str:
    return (
        f"💡 Sugerencias para el salón {codsalon}, semana {nsemana} de {year}: "
        f"1) Aumentar promociones cruzadas. 2) Mejorar retención de clientes nuevos."
    )
