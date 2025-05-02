import streamlit as st, pandas as pd, os
from utils.db import sb
from utils.metrics import curve_delta, picos_dataframe
st.set_page_config(page_title="Potencia crítica", layout="wide")

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

curves = sup.table("activities_metrics").select("date,pd_curve")\
        .eq("strava_id", athlete["strava_id"]).execute().data
if not curves:
    st.info("Aún no hay curvas.")
    st.stop()

dfc = pd.DataFrame(curves); dfc["date"] = pd.to_datetime(dfc["date"])
dfc = dfc.sort_values("date")

current = dfc.iloc[-1].pd_curve
past    = dfc.iloc[-31].pd_curve if len(dfc) >= 31 else dfc.iloc[0].pd_curve
delta   = curve_delta(current, past)

st.markdown("#### Cambio curva vs hace 30 d")
st.json({f"{int(k/60)} min": round(v, 1) for k, v in delta.items()})

# Picos potencia en el tiempo
metrics = sup.table("activities_metrics").select("date,best_5,best_60,best_300,best_1200")\
         .eq("strava_id", athlete["strava_id"]).execute().data
if metrics:
    pdf = picos_dataframe(pd.DataFrame(metrics))
    st.line_chart(pdf)
