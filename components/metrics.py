import streamlit as st
from utils.cp_model import calculate_cp_w_prime

def show_metrics(df):
    st.subheader("Métricas clave")
    cp, w_prime = calculate_cp_w_prime(df)
    st.metric("Potencia Crítica (CP)", f"{cp:.1f} W")
    st.metric("W'", f"{w_prime:.0f} J")