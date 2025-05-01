import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import os, sys, time, streamlit as st, pandas as pd
from utils.db import get_supabase
from utils.strava import exchange_code, get_activities, refresh_token
from utils import store_tokens, load_metrics   # si tus utilidades las tienes así

# ----- si tu archivo antes tenía más import, vuelve a añadirlos -----

# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
#  Ajuste para que Python encuentre 'utils/' aunque este archivo
#  siga dentro de pages/. Si ya moviste app.py a la raíz, puedes borrar
#  las dos líneas siguientes.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

def main():
    st.set_page_config(page_title="Panel Strava", layout="wide")

    sb = get_supabase()
    params = st.query_params          # sustituye a experimental_get_query_params

    # 1) FLUJO OAUTH ──────────────────────────────────────────────
    if "code" in params:
        raw_code = params["code"]
        code = raw_code[0] if isinstance(raw_code, list) else raw_code

        tokens = exchange_code(code)
        store_tokens(tokens)          # graba access/refresh en Supabase

        # Limpia la URL – evita reutilizar el code y el 400 “invalid”
        st.experimental_set_query_params()
        st.success("Cuenta conectada; recargando…")
        st.rerun()
        return                        # ← dentro de main, 8 espacios de sangría

    # 2) CARGA NORMAL DE LA APP ──────────────────────────────────
    # aquí pones tu selector de ciclista, gráficos, etc.
    # ---------------------------------------------------------
# 1) Identifica al usuario actual en la tabla athletes
user = sb.table("athletes").select("*").eq("access_token", tokens["access_token"]).single().execute().data
strava_id = user["strava_id"]

# 2) Si eres el entrenador (COACH_EMAIL), muestra selector
if user["coach_email"] == st.secrets["COACH_EMAIL"]:
    athletes = sb.table("athletes").select("strava_id,firstname,lastname").execute().data
    opciones = {f"{a['firstname']} {a['lastname']}": a["strava_id"] for a in athletes}
    nombre = st.sidebar.selectbox("Selecciona ciclista", opciones.keys())
    strava_id = opciones[nombre]

# 3) Carga y muestra métricas
df = load_metrics(strava_id)

if df.empty:
    st.info("Sin actividades todavía 😅")
else:
    st.subheader("Últimas actividades")
    st.dataframe(df[["name", "date", "distance", "moving_time", "average_watts"]])

    st.subheader("Mapa")
    if {"start_latitude", "start_longitude"}.issubset(df.columns):
        st.map(
            df.rename(columns={"start_latitude": "lat", "start_longitude": "lon"})[["lat", "lon"]]
        )

    st.subheader("Curva de potencia (TOP 10)")
    top10 = df.nlargest(10, "max_power")[["name", "max_power"]].set_index("name")
    st.bar_chart(top10)
# ---------------------------------------------------------

if __name__ == "__main__":
    main()
