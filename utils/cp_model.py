import numpy as np

def calculate_cp_w_prime(df):
    durations = df['duracion'] * 60
    powers = df['potencia']
    valid = durations > 0
    durations = durations[valid]
    powers = powers[valid]
    inv_d = 1 / durations
    coeffs = np.polyfit(inv_d, powers, 1)
    w_prime = coeffs[0]
    cp = coeffs[1]
    return cp, w_prime