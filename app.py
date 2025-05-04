import streamlit as st
from components.upload import upload_file
from components.metrics import show_metrics
from components.reports import generate_weekly_report
from components.charts import plot_charts

st.set_page_config(page_title="Cycling Coach Dashboard", layout="wide")
st.title("Cycling Coach Dashboard")

# 1. Subida de archivo
session_data = upload_file()

if session_data is not None:
    st.success("Datos cargados correctamente")
    # 2. Métricas y CP
    show_metrics(session_data)
    # 3. Informes y visualizaciones
    plot_charts(session_data)
    generate_weekly_report(session_data)