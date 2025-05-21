# sheets.py limpio: solo función para cargar hoja por GID

import pandas as pd

BASE_URL = "https://docs.google.com/spreadsheets/d/1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0/export?format=csv"

def cargar_hoja(gid):
    """
    Carga una hoja específica desde el Google Sheet central, dado su GID.
    Devuelve un DataFrame con columnas normalizadas y datos limpios.
    """
    url = f"{BASE_URL}&gid={gid}"
    df = pd.read_csv(url)

    # Normalizar nombres de columnas
    df.columns = [col.lower().strip().replace(" ", "_") for col in df.columns]

    # Limpiar valores no válidos
    df = df.replace(["(en blanco)", "", "NA", "n/a"], pd.NA)

    # Convertir numéricos
    for col in df.columns:
        df[col] = (
            df[col].astype(str)
            .str.replace(",", ".", regex=False)
            .str.strip()
        )
       try:
    df[col] = pd.to_numeric(df[col])
except Exception:
    pass


    return df

