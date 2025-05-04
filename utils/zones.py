import pandas as pd

def compute_power_zones(df):
    cp = df['potencia'].mean()
    zones = {
        'Z1': (0, 0.55 * cp),
        'Z2': (0.55 * cp, 0.75 * cp),
        'Z3': (0.75 * cp, 0.9 * cp),
        'Z4': (0.9 * cp, 1.05 * cp),
        'Z5': (1.05 * cp, 1.2 * cp),
    }
    zone_data = []
    for z, (low, high) in zones.items():
        time_in_zone = df[(df['potencia'] >= low) & (df['potencia'] < high)]['duracion'].sum()
        zone_data.append({'Zona': z, 'Tiempo (min)': time_in_zone})
    return pd.DataFrame(zone_data)