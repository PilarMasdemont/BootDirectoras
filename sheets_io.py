# sheets_io.py
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Ámbitos requeridos por Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Cargar credenciales desde el entorno
CREDENTIALS_PATH = "credentials.json"  # asegúrate de subir este archivo a Render y usar una variable de entorno si prefieres

credentials = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
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
