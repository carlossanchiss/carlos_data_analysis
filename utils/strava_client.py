import os, time
from stravalib.client import Client
CID=os.environ.get("STRAVA_CLIENT_ID")
CSEC=os.environ.get("STRAVA_CLIENT_SECRET")

def make(access_token=None, refresh_token=None, expires_at=None):
    c=Client()
    c.client_id=CID
    c.client_secret=CSEC
    if access_token:
        c.access_token=access_token
        c.refresh_token=refresh_token
        c.token_expires_at=expires_at
    return c

def exchange(code):
    c=Client()
    a,b,e=c.exchange_code_for_token(CID,CSEC,code)
    ath=c.get_athlete()
    return {"access_token":a,"refresh_token":b,"expires_at":e,"athlete":ath}
