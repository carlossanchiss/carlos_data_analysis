import streamlit as st
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]

def generate_weekly_report(df):
    st.subheader("Informe semanal")
    summary = df.tail(7).describe().to_string()
    prompt = f"Genera un resumen del entrenamiento semanal en lenguaje natural con base en esto:\n{summary}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un entrenador experto en ciclismo."},
                {"role": "user", "content": prompt}
            ]
        )
        st.write(response.choices[0].message.content)
    except Exception as e:
        st.error("Error generando informe: " + str(e))