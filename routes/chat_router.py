from memory import obtener_contexto, actualizar_contexto
from dispatcher import despachar_intencion

router = APIRouter()

@router.post("")
async def chat(request: Request):
    body = await request.json()
    mensaje_usuario = body.get("mensaje", "")
    codsalon = body.get("codsalon")
    intencion_info = clasificar_intencion_completa(mensaje_usuario)
    intencion = intencion_info["intencion"]

    # Detectar proceso incluso si la intención no está clara
    nombre_proceso = intencion_info.get("proceso") or extraer_nombre_proceso_desde_alias(mensaje_usuario)
    if not nombre_proceso:
        nombre_proceso = extraer_nombre_proceso(mensaje_usuario)

    # Validar fecha
    fecha_raw = extraer_fecha_desde_texto(mensaje_usuario)
    fecha = fecha_raw if fecha_raw != "FECHA_NO_VALIDA" else None

    # Responder por proceso si se detecta
    if nombre_proceso:
        respuesta = consultar_proceso(nombre_proceso, mensaje_usuario)
        return {"respuesta": f"Hola, soy Mont Dirección.\n\n{respuesta}"}

    # Enviar a dispatcher si no se detectó proceso
    resultado = despachar_intencion(
        intencion=intencion,
        texto_usuario=mensaje_usuario,
        fecha=fecha,
        codsalon=codsalon,
        codempleado=extraer_codempleado(mensaje_usuario),
        kpi=detectar_kpi(mensaje_usuario),
        sesion=obtener_contexto(codsalon),
    )

    return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado or 'Estoy pensando cómo responderte mejor.'}"}







