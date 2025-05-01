import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from utils import get_supabase, store_tokens, load_metrics, exchange_code, get_activities

def main() -> None:
    st.set_page_config(page_title="Panel Strava", layout="wide")
    sb = get_supabase()

    # ─── 1) FLUJO OAUTH ─────────────────────────────────────
    qp = st.query_params
    if "code" in qp:
        code = qp.pop("code")[0]
        tokens = exchange_code(code)
        store_tokens(tokens)
        st.session_state["strava_id"] = tokens["athlete"]["id"]
        st.success("✅ Cuenta conectada, recargando…")
        st.rerun()
        return

    # ─── 2) LOGIN si falta sesión ────────────────────────────
    if "strava_id" not in st.session_state:
        auth_url = (
            "https://www.strava.com/oauth/authorize"
            f"?client_id={os.environ['STRAVA_CLIENT_ID']}"
            "&response_type=code"
            f"&redirect_uri={st.secrets['REDIRECT_URI']}"
            "&scope=read,activity:read_all"
            "&approval_prompt=auto"
        )
        st.markdown(f"[🔑 Inicia sesión con Strava]({auth_url})")
        return

    sid = st.session_state["strava_id"]

    # ─── 3) SELECTOR COACH ───────────────────────────────────
    coach_email = st.secrets.get("COACH_EMAIL", "")
    if coach_email:
        row = sb.table("athletes")\
                .select("coach_email")\
                .eq("strava_id", sid)\
                .single().execute().data
        if row and row.get("coach_email") == coach_email:
            atletas = sb.table("athletes")\
                       .select("strava_id, firstname, lastname")\
                       .execute().data
            opciones = {
                f"{a['firstname']} {a['lastname']}": a["strava_id"]
                for a in atletas
            }
            elegido = st.sidebar.selectbox("Selecciona ciclista", opciones)
            sid = opciones[elegido]

    # ─── 4) CARGAR Y MOSTRAR DATOS ───────────────────────────
    df = load_metrics(sid)
    if df.empty:
        st.info("Sin actividades todavía.")
        return

    st.subheader("Últimas actividades")
    st.dataframe(df[["name", "date", "distance", "moving_time", "average_watts"]])

    if {"lat", "lon"}.issubset(df.columns):
        st.subheader("Mapa")
        st.map(df[["lat", "lon"]])

    if "max_power" in df.columns:
        st.subheader("Top-10 potencia máxima")
        top10 = df.nlargest(10, "max_power")[["name", "max_power"]].set_index("name")
        st.bar_chart(top10)

if __name__ == "__main__":
    main()
