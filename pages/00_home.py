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
if "code" in st.query_params:
    token = exchange(st.query_params["code"])
    a = token["athlete"]
    sup.table("athletes").upsert({
        "strava_id": a.id,
        "firstname": a.firstname,
        "lastname": a.lastname,
        "access_token": token["access_token"],
        "refresh_token": token["refresh_token"],
         "expires_at":    int(tok["expires_at"]),   # ← convierte a int
        "coach_email": COACH,        # puedes cambiar esto si hay multi‑coach
    }, on_conflict="strava_id").execute()
    st.success("Cuenta vinculada. Recarga la página.")
    st.experimental_set_query_params()   # limpia la URL
    st.stop()

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
