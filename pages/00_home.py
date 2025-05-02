import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))
import streamlit as st, pandas as pd, os, datetime
from urllib.parse import urlencode
from utils.db import sb
from utils.strava_client import exchange, ensure_fresh
from utils.metrics import np_tss

st.set_page_config(page_title="Cycling‑AI · Home", layout="wide")
sup = sb()
COACH = os.environ.get("COACH_EMAIL", "")

# ── LOGIN STRAVA ───────────────────────────────────────────────────
def login_btn():
    url = "https://www.strava.com/oauth/authorize?" + urlencode({
        "client_id": os.environ["STRAVA_CLIENT_ID"],
        "redirect_uri": os.environ["REDIRECT_URI"],
        "response_type": "code",
        "scope": "read,activity:read_all",
        "approval_prompt": "auto",
    })
    st.markdown(f"[**Iniciar sesión con Strava**]({url})", unsafe_allow_html=True)

# Recibir el ?code=
# ── Manejo del retorno OAuth de Strava ─────────────────────────
if "code" in st.query_params:
    code = st.query_params["code"]              # <— código temporal que envía Strava

    # 1. Intercambiar el code por tokens y datos de atleta
    tok = exchange(code)                        # dict con access_token, refresh_token, expires_at, athlete
    ath = tok["athlete"]                        # objeto Athlete de stravalib

    # 2. Guardar / actualizar en Supabase
    sup.table("athletes").upsert(
        {
            "strava_id":   ath.id,
            "firstname":   ath.firstname,
            "lastname":    ath.lastname,
            "access_token":  tok["access_token"],
            "refresh_token": tok["refresh_token"],
            "expires_at":    int(tok["expires_at"]),   # ← bigint requerido
            "coach_email":   COACH or None,
        },
        on_conflict="strava_id",                # fusiona si ya existe
    ).execute()

    st.success("Cuenta vinculada. Recarga la página.")
    st.experimental_set_query_params()         # limpia ?code= de la URL
    st.stop()                                  # detiene la ejecución; la próxima recarga ya pasa del login

# ── SELECCIÓN DE USUARIO ──────────────────────────────────────────
email = st.sidebar.text_input("Tu email (coach usa el suyo):")
rows = sup.table("athletes").select("*").execute().data

if email == COACH and rows:
    opciones = {f"{r['firstname']} {r['lastname']}": r for r in rows}
    nombre = st.sidebar.selectbox("Selecciona ciclista", list(opciones))
    user = opciones[nombre]
else:
    user = next((r for r in rows if r["coach_email"] == email), None)
    if not user:
        login_btn()
        st.stop()

# ── CARGA DE MÉTRICAS ─────────────────────────────────────────────
m = sup.table("activities_metrics").select("*").eq("strava_id", user["strava_id"]).execute().data
if not m:
    st.info("Aún no hay métricas — espera a que corra el cron nightly.")
    st.stop()

df = pd.DataFrame(m)
df["date"] = pd.to_datetime(df["date"])

# KPIs últimos 30 días
last30 = df[df.date >= df.date.max() - pd.Timedelta(days=30)]
dist = round(last30.distance_km.sum(), 1)
time_h = round(last30.moving_time_min.sum() / 60, 1)
tss30 = int(last30.tss.sum())

col1, col2, col3 = st.columns(3)
col1.metric("Distancia 30 d (km)", dist)
col2.metric("Tiempo mov. 30 d (h)", time_h)
col3.metric("TSS 30 d", tss30)

# Mini‑PMC
pmc = df[["date", "ctl", "atl"]].set_index("date").sort_index()
st.line_chart(pmc)
