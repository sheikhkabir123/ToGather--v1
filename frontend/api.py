# frontend/api.py
import os
import json
from pathlib import Path
import requests

# ---- Config ----
BASE_URL = os.environ.get("TG_BASE_URL", "http://127.0.0.1:8000/api/")
if not BASE_URL.endswith("/"):
    BASE_URL += "/"

# Persist session token to a small file next to this script
_SESSION_FILE = Path(__file__).with_name(".session.json")

def _read_session():
    if _SESSION_FILE.exists():
        try:
            return json.loads(_SESSION_FILE.read_text())
        except Exception:
            return {}
    return {}

def _write_session(d):
    try:
        _SESSION_FILE.write_text(json.dumps(d))
    except Exception:
        pass

def get_token():
    return _read_session().get("token")

def set_token(token: str | None):
    data = _read_session()
    if token:
        data["token"] = token
    else:
        data.pop("token", None)
    _write_session(data)

def clear_session():
    try:
        if _SESSION_FILE.exists():
            _SESSION_FILE.unlink()
    except Exception:
        pass

def auth_headers():
    tok = get_token()
    return {"Authorization": f"Token {tok}"} if tok else {}

def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return {"status": resp.status_code, "text": resp.text}

# ---- Auth ----
def register(username: str, email: str, password: str):
    try:
        r = requests.post(
            BASE_URL + "auth/register/",
            json={"username": username, "email": email, "password": password},
            timeout=10,
        )
        if r.status_code in (200, 201):
            data = r.json()
            token = data.get("token")
            if token:
                set_token(token)
            return True, data
        return False, safe_json(r)
    except Exception as e:
        return False, {"detail": str(e)}

def login(username: str, password: str):
    try:
        r = requests.post(
            BASE_URL + "auth/login/",
            json={"username": username, "password": password},
            timeout=10,
        )
        if r.status_code in (200, 201):
            data = r.json()
            token = data.get("token")
            if token:
                set_token(token)
            return True, data
        return False, safe_json(r)
    except Exception as e:
        return False, {"detail": str(e)}

def me():
    """Return (ok, payload) for GET /auth/me/"""
    try:
        r = requests.get(BASE_URL + "auth/me/", headers=auth_headers(), timeout=8)
        if r.status_code == 200:
            return True, r.json()
        return False, safe_json(r)
    except Exception as e:
        return False, {"detail": str(e)}

# ---- Location ----
def update_location(latitude, longitude, accuracy=None, heading=None, speed=None):
    """POST /location/ with lat/lng and optional fields."""
    tok = get_token()
    if not tok:
        return False, {"detail": "Not logged in"}

    payload = {
        "latitude": float(latitude),
        "longitude": float(longitude),
    }
    if accuracy not in (None, ""):
        payload["accuracy"] = float(accuracy)
    if heading not in (None, ""):
        payload["heading"] = float(heading)
    if speed not in (None, ""):
        payload["speed"] = float(speed)

    try:
        r = requests.post(
            BASE_URL + "location/",
            json=payload,
            headers=auth_headers(),
            timeout=8,
        )
        if r.status_code in (200, 201):
            return True, r.json()
        return False, safe_json(r)
    except Exception as e:
        return False, {"detail": str(e)}

def get_buddies_locations():
    """GET /locations/ to fetch buddies' latest locations."""
    tok = get_token()
    if not tok:
        return False, {"detail": "Not logged in"}
    try:
        r = requests.get(
            BASE_URL + "locations/",
            headers=auth_headers(),
            timeout=8,
        )
        if r.status_code == 200:
            return True, r.json()
        return False, safe_json(r)
    except Exception as e:
        return False, {"detail": str(e)}
# ---- Events ----

def _event_auth_check():
    if not get_token():
        return False, {"detail": "Not logged in"}
    return True, None

def create_event(
    title: str,
    starts_at: str,
    description: str | None = None,
    ends_at: str | None = None,
    place_name: str | None = None,
    latitude: float | str | None = None,
    longitude: float | str | None = None,
    visibility: str = "buddies",
):
    """
    POST /events/create/
    starts_at / ends_at are ISO8601 strings, e.g. "2025-08-23T10:00:00Z"
    """
    ok, err = _event_auth_check()
    if not ok:
        return ok, err

    payload = {
        "title": title,
        "starts_at": starts_at,
        "visibility": visibility,
    }
    if description not in (None, ""):
        payload["description"] = description
    if ends_at not in (None, ""):
        payload["ends_at"] = ends_at
    if place_name not in (None, ""):
        payload["place_name"] = place_name
    if latitude not in (None, ""):
        payload["latitude"] = float(latitude)
    if longitude not in (None, ""):
        payload["longitude"] = float(longitude)

    try:
        r = requests.post(
            BASE_URL + "events/create/",
            json=payload,
            headers=auth_headers(),
            timeout=10,
        )
        if r.status_code in (200, 201):
            return True, r.json()
        return False, safe_json(r)
    except Exception as e:
        return False, {"detail": str(e)}

def events_feed():
    """GET /events/ — public/buddies feed (depending on visibility)."""
    ok, err = _event_auth_check()
    if not ok:
        return ok, err
    try:
        r = requests.get(BASE_URL + "events/", headers=auth_headers(), timeout=10)
        if r.status_code == 200:
            return True, r.json()
        return False, safe_json(r)
    except Exception as e:
        return False, {"detail": str(e)}

# (optional but useful)
def my_events():
    """GET /events/mine/ — events I created."""
    ok, err = _event_auth_check()
    if not ok:
        return ok, err
    try:
        r = requests.get(BASE_URL + "events/mine/", headers=auth_headers(), timeout=10)
        if r.status_code == 200:
            return True, r.json()
        return False, safe_json(r)
    except Exception as e:
        return False, {"detail": str(e)}

def attending_events():
    """GET /events/attending/ — events I’ve joined."""
    ok, err = _event_auth_check()
    if not ok:
        return ok, err
    try:
        r = requests.get(BASE_URL + "events/attending/", headers=auth_headers(), timeout=10)
        if r.status_code == 200:
            return True, r.json()
        return False, safe_json(r)
    except Exception as e:
        return False, {"detail": str(e)}

def event_detail(event_id: int):
    """GET /events/<id>/"""
    ok, err = _event_auth_check()
    if not ok:
        return ok, err
    try:
        r = requests.get(f"{BASE_URL}events/{event_id}/", headers=auth_headers(), timeout=10)
        if r.status_code == 200:
            return True, r.json()
        return False, safe_json(r)
    except Exception as e:
        return False, {"detail": str(e)}

def join_event(event_id: int):
    """POST /events/<id>/join/"""
    ok, err = _event_auth_check()
    if not ok:
        return ok, err
    try:
        r = requests.post(f"{BASE_URL}events/{event_id}/join/", headers=auth_headers(), timeout=10)
        if r.status_code in (200, 201):
            return True, safe_json(r)
        return False, safe_json(r)
    except Exception as e:
        return False, {"detail": str(e)}

def leave_event(event_id: int):
    """DELETE /events/<id>/leave/"""
    ok, err = _event_auth_check()
    if not ok:
        return ok, err
    try:
        r = requests.delete(f"{BASE_URL}events/{event_id}/leave/", headers=auth_headers(), timeout=10)
        if r.status_code in (200, 204):
            return True, {"detail": "left"}
        return False, safe_json(r)
    except Exception as e:
        return False, {"detail": str(e)}

def delete_event(event_id: int):
    """DELETE /events/<id>/"""
    ok, err = _event_auth_check()
    if not ok:
        return ok, err
    try:
        r = requests.delete(f"{BASE_URL}events/{event_id}/", headers=auth_headers(), timeout=10)
        if r.status_code in (200, 204):
            return True, {"detail": "deleted"}
        return False, safe_json(r)
    except Exception as e:
        return False, {"detail": str(e)}

def update_event(event_id: int, **fields):
    """PATCH /events/<id>/
    Accepts same keys as create_event (title, description, starts_at, ends_at, place_name, latitude, longitude, visibility).
    """
    ok, err = _event_auth_check()
    if not ok:
        return ok, err

    payload = {}
    for k, v in fields.items():
        if v in (None, ""):
            continue
        if k in ("latitude", "longitude"):
            payload[k] = float(v)
        else:
            payload[k] = v

    try:
        r = requests.patch(f"{BASE_URL}events/{event_id}/", json=payload, headers=auth_headers(), timeout=10)
        if r.status_code == 200:
            return True, r.json()
        return False, safe_json(r)
    except Exception as e:
        return False, {"detail": str(e)}
# ---- Location ----

def update_location(latitude, longitude, accuracy=None, heading=None, speed=None):
    """
    POST /location/ with your current location.
    All numeric params can be str or float.
    """
    if not get_token():
        return False, {"detail": "Not logged in"}

    payload = {
        "latitude": float(latitude),
        "longitude": float(longitude),
    }
    if accuracy not in (None, ""):
        payload["accuracy"] = float(accuracy)
    if heading not in (None, ""):
        payload["heading"] = float(heading)
    if speed not in (None, ""):
        payload["speed"] = float(speed)

    try:
        r = requests.post(BASE_URL + "location/", json=payload, headers=auth_headers(), timeout=10)
        if r.status_code in (200, 201):
            return True, safe_json(r)
        return False, safe_json(r)
    except Exception as e:
        return False, {"detail": str(e)}

def get_buddies_locations():
    """
    GET /locations/ : returns latest locations for you + your buddies.
    """
    if not get_token():
        return False, {"detail": "Not logged in"}
    try:
        r = requests.get(BASE_URL + "locations/", headers=auth_headers(), timeout=10)
        if r.status_code == 200:
            return True, r.json()
        return False, safe_json(r)
    except Exception as e:
        return False, {"detail": str(e)}

# optional: look up one buddy by username
def get_location_of(username: str):
    """
    GET /location/<username>/
    """
    if not get_token():
        return False, {"detail": "Not logged in"}
    try:
        r = requests.get(f"{BASE_URL}location/{username}/", headers=auth_headers(), timeout=10)
        if r.status_code == 200:
            return True, r.json()
        return False, safe_json(r)
    except Exception as e:
        return False, {"detail": str(e)}
