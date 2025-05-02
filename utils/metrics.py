import numpy as np
from scipy.optimize import curve_fit
import pandas as pd

# ─────────────────  Potencia Normalizada & TSS  ──────────────────
def np_tss(watts_array, ftp, duration_s):
    if ftp == 0:
        return np.nan, np.nan
    four_sec = np.convolve(watts_array, np.ones(30) / 30, "valid")
    npow = np.power(four_sec, 4).mean() ** 0.25
    IF   = npow / ftp
    tss  = (duration_s * npow * IF) / (ftp * 3600) * 100
    return npow, tss

# ─────────────────  Potencia Crítica (CP, W′)  ───────────────────
def _ms(t, cp, w_prime):
    return w_prime / t + cp         # modelo Monod‑Scherrer

def critical_power(best_pd_dict):
    t = np.array(list(best_pd_dict.keys()), dtype=float)
    p = np.array(list(best_pd_dict.values()), dtype=float)
    popt, _ = curve_fit(_ms, t, p, bounds=(0, np.inf))
    cp, w_prime = popt[0], popt[1]
    return cp, w_prime

# ─────────────────  Curva Duración‑Potencia 1‑60 min  ────────────
def power_duration_curve(watts):
    curve = {}
    for m in range(1, 61):          # 1 … 60 min
        window = m * 60
        if len(watts) < window:
            continue
        avg = np.convolve(watts, np.ones(window) / window, "valid").max()
        curve[window] = avg
    return curve                     # {duración_seg: W}

def curve_delta(cur_now, cur_past):
    return {
        k: (cur_now[k] - cur_past.get(k, cur_now[k])) / cur_past.get(k, cur_now[k]) * 100
        for k in cur_now
    }

def picos_dataframe(df_metrics, durations=(5, 60, 300, 1200)):
    cols = [f"best_{d}" for d in durations]
    out  = df_metrics[["date"] + cols].dropna()
    return out.set_index("date")
