import pandas as pd

def leer_kpis():
    sheet_id = "1-40eCYIUj8yKBC1w55ukAO45lLnL7gEm1-p_OLkL8Lk"
    gid = "0"  # Puedes cambiar esto si necesitas otra pestaña
    SHEET_URL = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&id={sheet_id}&gid={gid}"

    df = pd.read_csv(SHEET_URL)
    return df.to_dict(orient="records")

