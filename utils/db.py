
import os
from supabase import create_client, Client

def get_supabase() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL or SUPABASE_SERVICE_KEY env vars not set.")
    return create_client(url, key)

import time, pandas as pd

def store_tokens(tokens: dict):
    """Guarda / actualiza los tokens de Strava en la tabla athletes."""
    sb = get_supabase()
    data = {
        "strava_id": tokens["athlete"]["id"],
        "firstname": tokens["athlete"]["firstname"],
        "lastname": tokens["athlete"]["lastname"],
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "expires_at": tokens["expires_at"],
    }
    sb.table("athletes").upsert(data, on_conflict="strava_id").execute()

def load_metrics(strava_id: int) -> pd.DataFrame:
    """
    Devuelve un DataFrame con métricas básicas para el panel.
    Ahora mismo sólo devuelve actividades crudas como ejemplo.
    """
    sb = get_supabase()
    acts = (
        sb.table("activities")
          .select("*")
          .eq("strava_id", strava_id)
          .execute()
          .data
    )
    return pd.DataFrame(acts)
