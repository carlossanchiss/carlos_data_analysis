"""
Edge Function: `nightly_metrics`
RRULE: FREQ=DAILY;BYHOUR=2
"""
import os, json, numpy as np
from utils.db import sb
from utils.metrics import np_tss, critical_power, power_duration_curve

def handler(event, context):
    sup = sb()
    rows = sup.table("activities_raw").select("*").execute().data
    for r in rows:
        data = r["raw_json"]
        watts = np.array(data["watts"], dtype=float)
        duration = int(data["elapsed_time"])
        ftp = data.get("ftp", 250)

        npow, tss = np_tss(watts, ftp, duration)
        curve = power_duration_curve(watts)

        metrics = {
            "strava_id": r["strava_id"],
            "activity_id": r["id"],
            "date": data["start_date"][:10],
            "distance_km": data["distance"] / 1000,
            "moving_time_min": data["moving_time"] / 60,
            "np": npow,
            "tss": tss,
            "pd_curve": json.dumps(curve),
            "best_5": curve.get(5),
            "best_60": curve.get(60),
            "best_300": curve.get(300),
            "best_1200": curve.get(1200),
        }
        sup.table("activities_metrics").upsert(metrics).execute()
