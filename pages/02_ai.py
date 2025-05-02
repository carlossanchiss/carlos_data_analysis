import streamlit as st, pandas as pd, os
from utils.db import sb
from utils.ai import generate_workout_plan
st.set_page_config(page_title="AI Insights", layout="wide")

sup   = sb()
COACH = os.environ.get("COACH_EMAIL", "")
email = st.sidebar.text_input("Tu email (coach usa el suyo):")
ath   = sup.table("athletes").select("*").execute().data

if email == COACH and ath:
    opts = {f"{a['firstname']} {a['lastname']}": a for a in ath}
    athlete = opts[st.sidebar.selectbox("Ciclista", list(opts))]
else:
    athlete = next((a for a in ath if a["coach_email"] == email), None)
    if not athlete:
        st.error("Sin acceso.")
        st.stop()

ins = sup.table("ai_insights").select("*")\
      .eq("strava_id", athlete["strava_id"]).order("week").execute().data

st.markdown("## Informe semanal")
if ins:
    st.markdown(ins[-1]["weekly_summary"])
else:
    st.info("Aún no hay informe – se genera los lunes.")

st.markdown("## Generar plan de entreno IA")
goal = st.text_input("Escribe tu objetivo (ej.: mejorar 5‑min power, preparar carrera X)")
if st.button("Proponer entrenos") and goal:
    cp      = athlete.get("cp", 250)
    w_prime = athlete.get("w_prime", 15000)
    plan    = generate_workout_plan(goal, cp, w_prime)
    st.markdown(plan)
