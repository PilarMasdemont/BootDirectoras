# sheets_io.py
import pandas as pd
import gspread
import os
import json
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Cargar credenciales desde variable de entorno segura
credentials_info = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
client = gspread.authorize(credentials)

def cargar_hoja_por_nombre(sheet_id: str, pestaña: str) -> pd.DataFrame:
    """Carga una hoja específica por nombre de pestaña y devuelve un DataFrame"""
    sheet = client.open_by_key(sheet_id).worksheet(pestaña)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    return df

def guardar_hoja(sheet_id: str, pestaña: str, df: pd.DataFrame):
    """Sobrescribe toda la pestaña con el contenido del DataFrame"""
    try:
        sheet = client.open_by_key(sheet_id).worksheet(pestaña)
        sheet.clear()
        sheet.update([df.columns.values.tolist()] + df.fillna("").values.tolist())
    except Exception as e:
        print(f"❌ Error al guardar en Google Sheets: {e}")
