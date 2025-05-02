import openai, os, json
from pyod.models.iforest import IForest
import pandas as pd

openai.api_key = os.getenv("OPENAI_API_KEY", "")

# ─────────  Anomalías en potencia o cadencia  ─────────
def detect_anomalies(series):
    if len(series) < 30:
        return pd.Series([False] * len(series))
    model = IForest(contamination=0.05)
    model.fit(series.values.reshape(-1, 1))
    return pd.Series(model.labels_.astype(bool), index=series.index)

# ─────────  Informe Semanal LLM  ─────────
def weekly_report(kpis_dict):
    prompt = (
        "Eres entrenador de ciclismo. Resume en 4 párrafos los insights más importantes del rendimiento de la semana, incluyendo volumen, carga, nuevos picos de potencia, entrenamiento más exigente:\n"
        + json.dumps(kpis_dict, ensure_ascii=False)
    )
    r = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content

# ─────────  Plan de entreno IA  ─────────
def generate_workout_plan(goal, cp, w_prime):
    prompt = (
        f"Eres entrenador de ciclismo. Objetivo del atleta: {goal}. "
        f"CP={cp:.0f} W y W'={w_prime:.0f} kJ.\n"
        "Diseña 3 sesiones (nombre, duración, bloques, TSS objetivo) para la próxima semana y proporciona los archivos .zwo para cargarlos como workout en TrainingPeaks o IntervalsICU."
    )
    r = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content
