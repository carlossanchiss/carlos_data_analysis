import streamlit as st
import pandas as pd

def upload_file():
    file = st.file_uploader("Sube el archivo .csv del entrenamiento", type="csv")
    if file:
        df = pd.read_csv(file, parse_dates=['fecha'])
        df.sort_values('fecha', inplace=True)
        return df
    return None