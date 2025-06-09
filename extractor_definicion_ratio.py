def extraer_kpi(texto: str) -> str | None:
    texto_normalizado = texto.lower().replace(" ", "").replace("_", "")

    sinonimos_kpis = {
        "FacturacionSIva": [
            "facturacionsiniva", "ventasnetas", "ingresosnetos", "facturaciontotal", "ventas"
        ],
        "HorasFichadas": [
            "horasfichadas", "registrohoras", "tiempotrabajado", "horastrabajadas", "controlhorario"
        ],
        "RatioDesviacionTiempoTeorico": [
            "desviaciontiempo", "tiemporealvsplanificado", "desviacionteorica",
            "desviacionenlaplanificaciondeltiempo", "desviacionplanificacion", "desviaciondeltiempo"
        ],
        "RatioTiempoIndirecto": [
            "tiempoindirecto", "horasnoefectivas", "tiempoadministrativo",
            "tiempodetareasinternas", "tiempolimpieza", "tiempoinvisible"
        ],
        "RatioTicketsInferior20": [
            "ticketsmenores20", "ticketspequeños", "ventasinferiores20", "ventasbajas", "ventaspequenas"
        ],
        "TicketSIvaMedio": [
            "ticketpromedio", "ticketmedio", "ticketmediosiniva", "importemedio", "valormedioticket"
        ]
    }

    for kpi, sinonimos in sinonimos_kpis.items():
        for termino in sinonimos:
            if termino in texto_normalizado:
                return kpi
    return None
