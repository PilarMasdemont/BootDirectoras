# funciones/intencion_total.py

from funciones.intencion import clasificar_intencion as clasificar_kpi_o_producto
from funciones.intention_process import clasificar_intencion as clasificar_proceso

def clasificar_intencion_completa(texto: str) -> dict:
    """
    Clasifica la intención del mensaje de forma jerárquica:
    1. Primero prueba detectar KPIs o productos.
    2. Si no se detecta con claridad, intenta clasificar como proceso.
    """

    resultado_primario = clasificar_kpi_o_producto(texto)
    if resultado_primario["intencion"] not in ["general", "desconocida"]:
        return resultado_primario

    resultado_proceso = clasificar_proceso(texto)
    if resultado_proceso["intencion"] != "desconocida":
        return resultado_proceso

    # Si ninguno detectó claramente, devuelvo el primero
    return resultado_primario
