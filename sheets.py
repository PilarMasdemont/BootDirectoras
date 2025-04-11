import pandas as pd

# Enlace directo a la hoja pública
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-40eCYIUj8yKBC1w55ukAO45lLnL7gEm1-p_OLkL8Lk/export?format=csv&gid=0"

def leer_kpis():
    df = pd.read_csv(SHEET_URL)
    return df.to_dict(orient="records")
