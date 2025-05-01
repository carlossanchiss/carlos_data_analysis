import os, time
import pandas as pd
from supabase import create_client, Client

def get_supabase() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_KEY"]
    return create_client(url, key)

def store_tokens(tokens: dict) -> None:
    sb = get_supabase()
    data = {
        "strava_id": tokens["athlete"]["id"],
        "firstname": tokens["athlete"]["firstname"],
        "lastname": tokens["athlete"]["lastname"],
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "expires_at": tokens["expires_at"],
        "coach_email": os.getenv("COACH_EMAIL", ""),
    }
    sb.table("athletes").upsert(data, on_conflict="strava_id").execute()

def load_metrics(strava_id: int) -> pd.DataFrame:
    """Devuelve DataFrame con actividades (básico)."""
    sb = get_supabase()
    acts = (
        sb.table("activities")
          .select("*")
          .eq("strava_id", strava_id)
          .order("start_date_local", desc=True)
          .execute()
          .data
    )
    if acts:
        return pd.DataFrame(acts)

    # fallback: tira directo de Strava (máx 50) y devuelve normalizado
    ath = sb.table("athletes").select("access_token").eq(
        "strava_id", strava_id
    ).single().execute().data
    if not ath:
        return pd.DataFrame()

    from .strava import get_activities
    acts = get_activities(ath["access_token"], per_page=50)
    df = pd.json_normalize(acts)
    df.rename(
        columns={"start_date_local": "date",
                 "start_latitude": "lat",
                 "start_longitude": "lon"},
        inplace=True,
    )
    return df
