
import os, requests

CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")

import os, requests

CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")

import os, requests

CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")

def exchange_code(code):
    res = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
        },
        timeout=15,
    )
    # 👇  Esto imprime siempre el cuerpo que nos manda Strava
    print("⛔️ Strava reply:", res.status_code, res.text[:600])

    res.raise_for_status()          # deja que Streamlit marque el error
    return res.json()

def refresh_token(refresh_token):
    res = requests.post("https://www.strava.com/oauth/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    })
    res.raise_for_status()
    return res.json()

def get_activities(access_token, per_page=100):
    r = requests.get("https://www.strava.com/api/v3/athlete/activities",
                     headers={"Authorization": f"Bearer {access_token}"},
                     params={"per_page": per_page})
    r.raise_for_status()
    return r.json()
