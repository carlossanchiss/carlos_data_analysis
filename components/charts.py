import streamlit as st
import plotly.express as px
from utils.training_load import calculate_load_metrics
from utils.zones import compute_power_zones

def plot_charts(df):
    st.subheader("Evolución del entrenamiento")
    df_metrics = calculate_load_metrics(df)
    fig = px.line(df_metrics, x='fecha', y=['CTL', 'ATL', 'TSB'], title="CTL / ATL / TSB")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Zonas de potencia")
    zones = compute_power_zones(df)
    fig2 = px.bar(zones, x='Zona', y='Tiempo (min)', title="Distribución en zonas")
    st.plotly_chart(fig2, use_container_width=True)