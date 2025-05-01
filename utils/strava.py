import os, requests

CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")

def exchange_code(code: str) -> dict:
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
    print("↩︎ Strava token reply:", res.status_code, res.text[:400])
    res.raise_for_status()          # si 4xx/5xx, Streamlit lo captura
    return res.json()

def refresh_token(refresh_token: str) -> dict:
    res = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=15,
    )
    res.raise_for_status()
    return res.json()

def get_activities(access_token: str, per_page: int = 50) -> list:
    res = requests.get(
        "https://www.strava.com/api/v3/athlete/activities",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"per_page": per_page},
        timeout=15,
    )
    res.raise_for_status()
    return res.json()
