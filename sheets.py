import pandas as pd
import requests

def leer_kpis():
    sheet_id = "1-40eCYIUj8yKBC1w55ukAO45lLnL7gEm1-p_OLkL8Lk"
    gid = "1076160199"  # Pestaña: KPIs_DiariosS

    SHEET_URL = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    response = requests.get(SHEET_URL)

    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code}: {response.reason}")

    # Lee el CSV directamente desde la respuesta
    from io import StringIO
    df = pd.read_csv(StringIO(response.text))

    return df.to_dict(orient="records")
