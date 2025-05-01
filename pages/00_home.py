# pages/00_home.py
import os, sys
# ▸ añade la carpeta padre (donde está utils/) al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from utils.db import get_supabase, store_tokens, load_metrics   # ← asegúrate de que existen
from utils.strava import exchange_code                          # get_activities / refresh_token si luego los usas

def main() -> None:
    st.set_page_config(page_title="Panel Strava", layout="wide")
    sb = get_supabase()                      # conexión Supabase

    # ─────────────────── 1) FLUJO OAUTH ────────────────────
    params = st.query_params
    if "code" in params:                     # volvemos de Strava con ?code=…
        raw_code = params["code"]
        code = raw_code[0] if isinstance(raw_code, list) else raw_code

        tokens = exchange_code(code)         # POST /oauth/token
        store_tokens(tokens)                 # guarda/actualiza en tabla athletes

        # guarda strava_id en la sesión para la recarga “limpia”
        st.session_state["strava_id"] = tokens["athlete"]["id"]

        # elimina ?code= de la URL y recarga sin él
        st.query_params.clear()
        st.success("Cuenta conectada; recargando…")
        st.rerun()
        return

    # ──────────────── 2) COMPROBAR SESION ──────────────────
    if "strava_id" not in st.session_state:
        auth_url = (
            f"https://www.strava.com/oauth/authorize"
            f"?client_id={os.environ['STRAVA_CLIENT_ID']}"
            f"&response_type=code"
            f"&redirect_uri={st.secrets['REDIRECT_URI']}"
            "&scope=read,activity:read_all"
            "&approval_prompt=auto"
        )
        st.markdown(f"[🔑 Inicia sesión con Strava]({auth_url})")
        return

    strava_id = st.session_state["strava_id"]

    # ───────────── 3) SELECTOR COACH (OPCIONAL) ─────────────
    coach_email = st.secrets.get("COACH_EMAIL")
    if coach_email:
        # ¿el usuario logeado es el coach?
        row = (
            sb.table("athletes")
              .select("coach_email")
              .eq("strava_id", strava_id)
              .single()
              .execute()
              .data
        )
        if row and row.get("coach_email") == coach_email:
            atletas = (
                sb.table("athletes")
                  .select("strava_id, firstname, lastname")
                  .execute()
                  .data
            )
            opciones = {
                f"{a['firstname']} {a['lastname']}": a["strava_id"]
                for a in atletas
            }
            elegido = st.sidebar.selectbox("Selecciona ciclista", opciones)
            strava_id = opciones[elegido]

    # ─────────────── 4) CARGAR Y MOSTRAR DATOS ──────────────
    df = load_metrics(strava_id)
    if df.empty:
        st.warning("Aún no hay actividades para este atleta.")
        return

    st.subheader("Últimas actividades")
    st.dataframe(
        df[["name", "date", "distance", "moving_time", "average_watts"]]
    )

    st.subheader("Mapa")
    if {"lat", "lon"}.issubset(df.columns):
        st.map(df[["lat", "lon"]])

    st.subheader("Curva de potencia (TOP 10)")
    if "max_power" in df.columns:
        top10 = (
            df.nlargest(10, "max_power")[["name", "max_power"]]
              .set_index("name")
        )
        st.bar_chart(top10)

# ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
