from fastapi import APIRouter, Request, HTTPException
import logging
from manejar_peticion_chat import manejar_peticion_chat
from kpis import explicar_ratio, explicar_ratio_empleado
from explicar_producto import explicar_producto
from sesion import guardar_sesion

router = APIRouter()

@router.post("/chat")
async def procesar_chat(request: Request):
    datos_entrada = await request.json()
    texto_usuario = datos_entrada.get("mensaje", "")
    ip_usuario = request.client.host

    logging.info(f"📥 Petición recibida de {ip_usuario}: '{texto_usuario}'")

    try:
        datos = manejar_peticion_chat(texto_usuario, ip_usuario)
    except Exception as e:
        logging.error(f"❌ Error en manejo de petición: {e}")
        raise HTTPException(status_code=500, detail="Error interno al interpretar la petición")

    intencion = datos.get("intencion")
    fecha = datos.get("fecha")
    cod_salon = datos.get("cod_salon")
    empleado = datos.get("empleado")
    kpi_detectado = datos.get("kpi")
    sesion = datos.get("sesion", {})

    logging.info(f"🧠 Intención: {intencion}")
    logging.info(f"📅 Fecha extraída: {fecha}")
    logging.info(f"🏢 Salón: {cod_salon}")
    logging.info(f"👤 Empleado: {empleado}")
    logging.info(f"📊 KPI: {kpi_detectado}")
    logging.info(f"📂 Sesión cargada: {sesion}")

    # --- Procesar explicación de producto primero ---
    if intencion == "explicar_producto":
        nombre_producto = datos.get("nombre_producto")
        if nombre_producto:
            try:
                resultado = explicar_producto(nombre_producto)
                guardar_sesion(sesion)
                return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}
            except Exception as e:
                logging.error(f"❌ Error al procesar producto: {e}")
                raise HTTPException(status_code=500, detail="Error al procesar el producto.")
        else:
            return {"respuesta": "No pude identificar el producto del que me hablas. ¿Puedes repetirlo con más detalle?"}

    # --- Procesar explicación de ratio general ---
    if intencion == "explicar_ratio":
        try:
            resultado = explicar_ratio(fecha, cod_salon, kpi_detectado)
            guardar_sesion(sesion)
            return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}
        except Exception as e:
            logging.error(f"❌ Error al explicar ratio: {e}")
            raise HTTPException(status_code=500, detail="Error al procesar la solicitud de KPI.")

    # --- Procesar explicación de ratio de empleado ---
    if intencion == "explicar_ratio_empleado":
        try:
            resultado = explicar_ratio_empleado(fecha, cod_salon, empleado, kpi_detectado)
            guardar_sesion(sesion)
            return {"respuesta": f"Hola, soy Mont Dirección.\n\n{resultado}"}
        except Exception as e:
            logging.error(f"❌ Error al explicar ratio empleado: {e}")
            raise HTTPException(status_code=500, detail="Error al procesar la solicitud de KPI por empleado.")

    # --- Intención no reconocida ---
    return {"respuesta": "No entendí tu petición. ¿Puedes reformularla, por favor?"}
