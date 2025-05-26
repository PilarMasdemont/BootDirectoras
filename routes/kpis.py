from fastapi import APIRouter, HTTPException
from sheets import cargar_hoja
import pandas as pd

router = APIRouter()

@router.get("/kpis/30dias")
def get_kpis_diarios(codsalon: str):
    try:
        df = cargar_hoja("1882861530")
        datos_filtrados = df[df['codsalon'].astype(str) == codsalon]
        return datos_filtrados.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/kpis/semanal")
def get_kpis_semanales(codsalon: str):
    try:
        df = cargar_hoja("72617950")
        datos_filtrados = df[df['codsalon'].astype(str) == codsalon]
        return datos_filtrados.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/kpis/mensual")
def get_kpis_mensuales(codsalon: str):
    try:
        df = cargar_hoja("1194190690")
        datos_filtrados = df[df['codsalon'].astype(str) == codsalon]
        return datos_filtrados.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))