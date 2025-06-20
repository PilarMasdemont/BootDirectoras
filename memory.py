# funciones/memory.py

# Diccionario global de contexto por codsalon
estado_usuarios = {}

def obtener_contexto(codsalon: str) -> dict:
    return estado_usuarios.get(codsalon, {})

def actualizar_contexto(codsalon: str, clave: str, valor: str):
    if codsalon not in estado_usuarios:
        estado_usuarios[codsalon] = {}
    estado_usuarios[codsalon][clave] = valor

def limpiar_contexto(codsalon: str):
    if codsalon in estado_usuarios:
        del estado_usuarios[codsalon]
