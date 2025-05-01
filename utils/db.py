
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

import pandas as pd
from datetime import datetime

def load_metrics(strava_id: int) -> pd.DataFrame:
    """
    Devuelve un DataFrame con las actividades y métricas básicas
    almacenadas en la tabla `activities`. Si todavía no tienes
    esa tabla, puedes devolver directamente las actividades
    recién descargadas de Strava.
    """
    sb = get_supabase()

    # ----- intenta cargar ya guardado en Supabase -----
    resp = (
        sb.table("activities")
          .select("*")
          .eq("strava_id", strava_id)
          .order("start_date_local", desc=True)
          .execute()
    )
    data = resp.data

    if data:                          # hay datos en la DB
        return pd.DataFrame(data)

    # ----- si no hay nada en DB, pide directo a Strava -----
    ath = sb.table("athletes").select("*").eq("strava_id", strava_id).single().execute().data
    access_token = ath["access_token"]

    from utils.strava import get_activities
    acts = get_activities(access_token, per_page=50)

    # conviértelo en DataFrame
    df = pd.json_normalize(acts)
    df.rename(columns={"start_date_local": "date"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df

