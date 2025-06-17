# funciones/explicar_producto.py

from funciones.consultar_producto_con_chatgpt import consultar_producto_chatgpt
from google_sheets_session import buscar_producto_por_nombre_o_alias

def explicar_producto(nombre_producto: str, atributo: str = None) -> str:
    # 1. Intenta usar el JSON local primero
    respuesta_local = consultar_producto_chatgpt(nombre_producto, atributo)
    if "No tengo información sobre el producto" not in respuesta_local:
        return respuesta_local

    # 2. Si no se encuentra en el JSON, consulta en Google Sheets
    datos = buscar_producto_por_nombre_o_alias(nombre_producto)
    if not datos:
        return f"No encontré información sobre el producto '{nombre_producto}'. ¿Podrías verificar el nombre o darme más detalles?"

    def seccion(titulo: str, contenido: str) -> str:
        return f"\n\n**{titulo}**\n{contenido.strip()}" if contenido and str(content := contenido).strip() else ""

    respuesta = f"**{datos.get('nombre', '').strip()}** ({datos.get('marca', '').strip()})"

    # 🧴 Cómo se usa
    respuesta += seccion("🧴 Cómo se usa", datos.get("modo_uso", ""))

    # ✨ Beneficios esperados
    beneficios = [
        datos.get("beneficio_1", ""),
        datos.get("beneficio_2", ""),
        datos.get("beneficio_3", ""),
        datos.get("beneficio_4", "")
    ]
    beneficios = [b.strip() for b in beneficios if b.strip()]
    if beneficios:
        respuesta += seccion("✨ Beneficios esperados", "\n– " + "\n– ".join(beneficios))

    # 💡 Argumentos de venta (ingredientes)
    if datos.get("ingredientes"):
        respuesta += seccion("💡 Ingredientes clave", datos.get("ingredientes"))

    # 🛑 Precauciones
    if "precauciones" in datos:
        respuesta += seccion("🛑 Precauciones", datos.get("precauciones", ""))

    # 🗣️ Testimonios
    comentarios = [
        datos.get("comentario_1", ""),
        datos.get("comentario_2", ""),
        datos.get("comentario_3", "")
    ]
    comentarios = [c.strip() for c in comentarios if c.strip()]
    if comentarios:
        respuesta += seccion("🗣️ Opiniones de otras directoras", "\n– " + "\n– ".join(comentarios))

    return respuesta.strip()


