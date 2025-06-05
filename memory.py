# memory.py — memoria en RAM para sesiones temporales

from collections import defaultdict

# Diccionario de contexto por usuario/IP
user_context = defaultdict(dict)

# Funciones auxiliares para cargar y guardar sesión

def cargar_sesion(ip_usuario):
    return user_context[ip_usuario]

def guardar_sesion(sesion):
    ip = sesion.get("ip_usuario")
    if ip:
        user_context[ip] = sesion
