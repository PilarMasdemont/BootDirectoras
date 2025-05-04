# funciones/base.py
import pandas as pd
from funciones.utils import cargar_hoja

def leer_kpis(year, nsemana, codsalon, tipo="semana"):
    """Carga y filtra los KPIs desde Google Sheets según parámetros"""
    df = cargar_hoja(tipo)
    df = df[(df['año'] == year) & (df['nsemana'] == nsemana) & (df['cod_salon'] == codsalon)]
    return df
