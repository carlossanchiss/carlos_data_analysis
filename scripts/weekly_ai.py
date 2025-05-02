"""
Edge Function: `weekly_ai`
RRULE: FREQ=WEEKLY;BYDAY=MO;BYHOUR=3
"""
import datetime, json
from utils.db import sb
from utils.ai import weekly_report

def handler(event, context):
    sup = sb()
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    athletes = sup.table("athletes").select("*").execute().data
    for a in athletes:
        kpi = sup.rpc("compute_week_kpis", {"p_strava_id": a["strava_id"]}).data  # suponiendo función SQL
        report = weekly_report(kpi)
        sup.table("ai_insights").upsert({
            "strava_id": a["strava_id"],
            "week": monday.isoformat(),
            "weekly_summary": report,
        }).execute()
