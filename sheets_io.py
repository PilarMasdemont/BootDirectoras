# sheets_io.py
import pandas as pd
import gspread
import os
import json
import logging
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Cargar credenciales desde variable de entorno segura
credentials_info = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
client = gspread.authorize(credentials)

def cargar_hoja_por_nombre(sheet_id: str, pestaña: str) -> pd.DataFrame:
    """
    Carga una hoja específica por nombre de pestaña y devuelve un DataFrame.
    Normaliza los nombres de columna sin usar accesores .str para evitar errores de tipo.
    """
    try:
        logger.info(f"[GSHEETS] Cargando hoja '{pestaña}' desde documento {sheet_id}")
        sheet = client.open_by_key(sheet_id).worksheet(pestaña)
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        df.columns = [str(col).lower().replace(" ", "_") for col in df.columns]
        logger.info(f"[GSHEETS] Hoja cargada: {len(df)} filas, columnas: {df.columns.tolist()}")
        return df
    except Exception as e:
        logger.error(f"[GSHEETS] ❌ Error al cargar hoja '{pestaña}' del documento {sheet_id}: {e}")
        raise

def guardar_hoja(sheet_id: str, pestaña: str, df: pd.DataFrame):
    """
    Sobrescribe toda la pestaña con el contenido del DataFrame.
    """
    try:
        logger.info(f"[GSHEETS] Guardando hoja '{pestaña}' en documento {sheet_id} con {len(df)} filas")
        sheet = client.open_by_key(sheet_id).worksheet(pestaña)
        sheet.clear()
        sheet.update([df.columns.values.tolist()] + df.fillna("").values.tolist())
        logger.info("[GSHEETS] Guardado exitoso")
    except Exception as e:
        logger.error(f"[GSHEETS] ❌ Error al guardar en hoja '{pestaña}' del documento {sheet_id}: {e}")
