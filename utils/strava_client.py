import os, time
from stravalib.client import Client

CID = os.environ["STRAVA_CLIENT_ID"]
CSEC = os.environ["STRAVA_CLIENT_SECRET"]

def make(access_token=None, refresh_token=None, expires_at=None):
    c = Client()
    c.client_id, c.client_secret = CID, CSEC
    if access_token:
        c.access_token = access_token
        c.refresh_token = refresh_token
        c.token_expires_at = expires_at
    return c

def exchange(code):
    c = Client()
    at, rt, exp = c.exchange_code_for_token(CID, CSEC, code)
    return {"access_token": at, "refresh_token": rt, "expires_at": exp, "athlete": c.get_athlete()}

def ensure_fresh(row):
    if row["expires_at"] > int(time.time()) + 300:
        return row["access_token"]
    c = make(row["access_token"], row["refresh_token"], row["expires_at"])
    new = c.refresh_access_token(client_id=CID, client_secret=CSEC, refresh_token=c.refresh_token)
    return new["access_token"]
