import pandas as pd
import requests
from io import StringIO

def leer_kpis():
    sheet_id = "1-40eCYIUj8yKBC1w55ukAO45lLnL7gEm1-p_OLkL8Lk"
    gid = "0"  # Puedes cambiar esto si necesitas leer otra pestaña

    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code}: {response.reason}")

    df = pd.read_csv(StringIO(response.text))
    return df.to_dict(orient="records")
