import os
import io
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from google.oauth2 import service_account

# Cargar credenciales desde variable de entorno
GOOGLE_CREDENTIALS = json.loads(os.environ["1kQUa22fp26t8MO_n4P5anqU82B14aF3A"])
SCOPES = ["https://www.googleapis.com/auth/drive"]

credentials = service_account.Credentials.from_service_account_info(
    GOOGLE_CREDENTIALS, scopes=SCOPES
)

# Crear servicio Drive
service = build('drive', 'v3', credentials=credentials)

# Obtener folder ID desde variable de entorno
FOLDER_ID = os.environ["GOOGLE_DRIVE_FOLDER_ID"]

def construir_nombre_archivo(ip, fecha):
    """Crea el nombre del archivo .json según IP y fecha"""
    return f"{fecha}__IP_{ip}.json"

def guardar_estado_sesion(data, ip, fecha):
    """
    Guarda el estado de sesión en Google Drive (lo crea o lo sobreescribe).
    """
    nombre_archivo = construir_nombre_archivo(ip, fecha)
    
    # Convertimos el dict a JSON binario
    json_data = json.dumps(data).encode('utf-8')
    media = MediaIoBaseUpload(io.BytesIO(json_data), mimetype='application/json')

    # Buscar archivo por nombre en la carpeta
    query = f"name='{nombre_archivo}' and '{FOLDER_ID}' in parents and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields="files(id)").execute()
    files = results.get('files', [])

    if files:
        # Si ya existe, actualizamos
        file_id = files[0]['id']
        service.files().update(fileId=file_id, media_body=media).execute()
    else:
        # Si no existe, creamos
        file_metadata = {
            'name': nombre_archivo,
            'parents': [FOLDER_ID],
            'mimeType': 'application/json'
        }
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()

def cargar_estado_sesion(ip, fecha):
    """
    Carga el estado de sesión desde Google Drive, o devuelve None si no existe.
    """
    nombre_archivo = construir_nombre_archivo(ip, fecha)
    query = f"name='{nombre_archivo}' and '{FOLDER_ID}' in parents and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields="files(id)").execute()
    files = results.get('files', [])

    if not files:
        return None

    file_id = files[0]['id']
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    fh.seek(0)
    return json.load(fh)
