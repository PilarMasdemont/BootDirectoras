def extraer_kpi(texto: str) -> str | None:
    texto_normalizado = texto.lower().replace(" ", "").replace("_", "")

    sinonimos_kpis = {
        "FacturacionSIva": ["facturacionsiniva", "ventasnetas", "ingresosnetos"],
        "HorasFichadas": ["horasfichadas", "registrohoras", "tiempotrabajado"],
        "RatioDesviacionTiempoTeorico": ["desviaciontiempo", "tiemporealvsplanificado", "desviacionteorica"],
        "RatioTiempoIndirecto": ["tiempoindirecto", "horasnoefectivas", "tiempoadministrativo"],
        "RatioTicketsInferior20": ["ticketsmenores20", "ticketspequeños", "ventasinferiores20"],
        "TicketSIvaMedio": ["ticketpromedio", "ticketmedio", "ticketmediosiniva"]
    }

    for kpi, sinonimos in sinonimos_kpis.items():
        for termino in sinonimos:
            if termino in texto_normalizado:
                return kpi
    return None

