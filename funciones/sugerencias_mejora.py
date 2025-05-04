# funciones/sugerencias_mejora.py
from funciones.base import leer_kpis

def sugerencias_mejora(year: int, nsemana: int, codsalon: int, tipo: str = "semana") -> str:
    df = leer_kpis(year, nsemana, codsalon, tipo)
    if df.empty:
        return "No hay datos suficientes para sugerencias."

    sugerencias = []
    if 'ticket_medio' in df.columns and df['ticket_medio'].mean() < 15:
        sugerencias.append("💡 Aumentar el ticket medio con servicios complementarios.")
    if 'clientes' in df.columns and df['clientes'].mean() < 50:
        sugerencias.append("📢 Promover campañas para atraer más clientes.")
    if 'productividad' in df.columns and df['productividad'].mean() < 0.5:
        sugerencias.append("⚙️ Revisar la asignación de tiempos del equipo.")

    return "\n".join(sugerencias) if sugerencias else "✅ Los KPIs actuales están dentro de parámetros saludables."
