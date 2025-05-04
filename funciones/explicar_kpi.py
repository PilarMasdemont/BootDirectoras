# funciones/explicar_kpi.py
def explicar_kpi(nombre_kpi: str, **kwargs) -> str:
    explicaciones = {
        "clientes": "Número total de personas atendidas en la semana.",
        "ticket_medio": "Promedio de ingreso por cliente.",
        "ingresos": "Suma total facturada por el salón.",
        "productividad": "Relación entre ingresos y tiempo trabajado.",
    }
    return explicaciones.get(nombre_kpi.lower(), f"No tengo una definición para el KPI '{nombre_kpi}'.")
