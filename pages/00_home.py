import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from utils.db import get_supabase
from utils.strava import get_activities, exchange_code, refresh_token
import os, time, datetime

st.set_page_config(page_title="Análisis Strava", layout="wide")

sb = get_supabase()

CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
REDIRECT_URI = os.environ.get("REDIRECT_URI", "")

def store_tokens(tokens):
    sb.table("athletes").upsert({
        "strava_id": tokens["athlete"]["id"],
        "firstname": tokens["athlete"]["firstname"],
        "lastname": tokens["athlete"]["lastname"],
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "expires_at": tokens["expires_at"]
    }, on_conflict="strava_id").execute()

def ensure_token(row):
    if row["expires_at"] > int(time.time()):
        return row["access_token"]
    new = refresh_token(row["refresh_token"])
    sb.table("athletes").update({
        "access_token": new["access_token"],
        "refresh_token": new["refresh_token"],
        "expires_at": new["expires_at"]
    }).eq("strava_id", row["strava_id"]).execute()
    return new["access_token"]

def main():
    st.title("Panel de análisis Strava (multi‑ciclista)")

    params = st.query_params  
    if "code" in params:
        code = params["code"][0]
        tokens = exchange_code(code, REDIRECT_URI)
        store_tokens(tokens)
        st.success("Cuenta conectada. Pulsa F5 o recarga la página.")
        st.stop()

    coach_email = os.environ.get("COACH_EMAIL", "")

    email = st.text_input("Introduce tu correo (si eres el coach pon el tuyo):")

    athletes = sb.table("athletes").select("*").execute().data

    if email == coach_email and athletes:
        options = {f"{a['firstname']} {a['lastname']}": a for a in athletes}
        seleccionado = st.sidebar.selectbox("Selecciona ciclista", list(options))
        athlete = options[seleccionado]
    else:
        # intenta buscar en athletes
        athlete = next((a for a in athletes if a.get("email")==email), None)
        if not athlete:
            login_url = f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope=read,activity:read_all&approval_prompt=auto"
            st.markdown(f"[Iniciar sesión con Strava]({login_url})")
            st.stop()

    access_token = ensure_token(athlete)
    acts = get_activities(access_token, per_page=50)
    df = pd.DataFrame(acts)
    if df.empty:
        st.info("Sin actividades.")
        return
    st.subheader("Últimas actividades")
    st.dataframe(df[["name","start_date_local","distance","moving_time","average_watts"]])
    st.map(df.rename(columns={"start_latlng":"latlon"})["latlon"].dropna().explode().dropna().apply(lambda x: {"lat": x[0], "lon": x[1]}) if "start_latlng" in df.columns else df.head(0))

if __name__ == "__main__":
    main()
