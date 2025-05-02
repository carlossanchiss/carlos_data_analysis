"""
Edge Function: `sync_strava`
RRULE: FREQ=HOURLY;INTERVAL=3
"""
import os, supabase_py
from utils.db import sb
from utils.strava_client import fetch_activities, ensure_token

def handler(event, context):
    sup = sb()
    athletes = sup.table("athletes").select("*").execute().data
    for a in athletes:
        token = ensure_token(a)
        acts  = fetch_activities(token, per_page=200)
        for act in acts:
            sup.table("activities_raw").upsert({
                "id": act.id,
                "strava_id": a["strava_id"],
                "raw_json": act.to_dict(),
                "start_date": act.start_date,
            }).execute()
