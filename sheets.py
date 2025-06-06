import pandas as pd
import logging

BASE_URL = "https://docs.google.com/spreadsheets/d/1RjMSyAnstLidHhziswtQWPCwbvFAHYFtA30wsg2BKZ0/export?format=csv"

logger = logging.getLogger(__name__)

def cargar_hoja(gid):
    """
    Carga una hoja específica desde el Google Sheet central, dado su GID.
    Devuelve un DataFrame con columnas normalizadas y datos limpios.
    """
    url = f"{BASE_URL}&gid={gid}"
    logger.info(f"[SHEETS] Cargando hoja con GID: {gid}")
    try:
        df = pd.read_csv(url)
        logger.info(f"[SHEETS] Columnas originales: {df.columns.tolist()}")

        # Normalizar nombres de columnas
        df.columns = [col.lower().strip().replace(" ", "_") for col in df.columns]
        logger.info(f"[SHEETS] Columnas normalizadas: {df.columns.tolist()}")

        # Limpiar valores no válidos
        df = df.replace(["(en blanco)", "", "NA", "n/a"], pd.NA)

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

    except Exception as e:
        logger.error(f"[SHEETS] ❌ Error cargando hoja con GID {gid}: {e}")
        raise
