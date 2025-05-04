import pandas as pd

def calculate_load_metrics(df):
    df['ATL'] = df['tss'].ewm(span=7).mean()
    df['CTL'] = df['tss'].ewm(span=42).mean()
    df['TSB'] = df['CTL'] - df['ATL']
    return df