import pandas as pd
import requests
from io import StringIO
import numpy as np

def leer_kpis():
    sheet_id = "1-40eCYIUj8yKBC1w55ukAO45lLnL7gEm1-p_OLkL8Lk"
    gid = "1076160199"

    SHEET_URL = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    response = requests.get(SHEET_URL)
    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code}: {response.reason}")

    df = pd.read_csv(StringIO(response.text))

    # ✨ Reemplazar valores que no son válidos en JSON
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna("null", inplace=True)  # También podrías usar 0 o "" según tu caso

    return df.to_dict(orient="records")

