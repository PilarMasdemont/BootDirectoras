import pandas as pd
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from io import StringIO
import requests

# 🔢 Autenticación para Google Sheets desde variable de entorno
alcance = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
credenciales_info = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
credenciales = ServiceAccountCredentials.from_json_keyfile_dict(credenciales_info, alcance)
cliente = gspread.authorize(credenciales)


# 📂 Lectura de hoja desde URL con GID público (sheets.py original)
def cargar_hoja(gid):
    url = f"https://docs.google.com/spreadsheets/d/1AYpA_9RMDTc6ZAvJd4BhqpvMDT1dlfdQ_M7uNtvhEXM/export?format=csv&gid={gid}"
    response = requests.get(url)
    response.encoding = 'utf-8'
    df = pd.read_csv(StringIO(response.text))
    df.columns = df.columns.str.lower()
    print("\U0001F4CB Columnas normalizadas:", df.columns.tolist())
    return df


# 📊 Lectura por nombre de hoja (sheets_io original)
def cargar_hoja_por_nombre(nombre_documento, nombre_hoja):
    sheet = cliente.open(nombre_documento).worksheet(nombre_hoja)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df.columns = df.columns.str.lower()
    return df


# 🔧 Escritura en hoja de Google Sheets (actualizar tabla)
def guardar_hoja(nombre_documento, nombre_hoja, df):
    try:
        sheet = cliente.open(nombre_documento).worksheet(nombre_hoja)
        sheet.clear()
        sheet.update([df.columns.values.tolist()] + df.values.tolist())
        print("✅ Hoja actualizada correctamente.")
    except Exception as e:
       print(f"❌ Error al guardar hoja: {e}")

