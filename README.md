# ToGather — v1

Minimal, working base for **ToGather**: people traveling separately but together — share live locations with buddies, form a group, and see a common destination.

---

## ✨ v1 Features

* **Auth (basic):** Sign up / Login (Firebase Auth or Django auth)
* **Profile:** Name + email
* **Location sharing:** Fetch own GPS location (Plyer) and show on map
* **Buddies:** Add buddy by email/username; see buddy markers
* **Group travel:** Create/join group via code; leader sets destination visible to all

---

## 🧱 Tech Stack

* **Mobile:** Kivy (Python), Plyer (GPS), simple Map view (WebView/Leaflet or Google Maps)
* **Backend:** Django + Django REST Framework
* **Database/Sync:** Firebase Realtime DB or Firestore (fast realtime sync)

---

## 📁 Project Structure

```
v1/
 ├─ backend/
 │   ├─ core/           # Django project (settings, urls, asgi/wsgi)
 │   ├─ server/         # Django app (API endpoints)
 │   ├─ manage.py
 │   └─ requirements.txt
 └─ mobile/
     ├─ main.py         # Kivy entry
     ├─ screens/        # login.kv, home.kv, map.kv
     ├─ services/       # auth.py, location.py
     └─ requirements.txt
```

---

## 🚀 Quickstart

### 1) Clone

```bash
git clone https://github.com/sheikhkabir123/ToGather--v1.git
cd ToGather--v1/v1
```

### 2) Backend Setup (Django)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # on macOS/Linux
# .\venv\Scripts\activate # on Windows PowerShell
pip install -r requirements.txt

# Create .env (example below), then run migrations
python manage.py migrate
python manage.py runserver
```

**`backend/requirements.txt` (suggested):**

```
django
djangorestframework
firebase-admin
python-dotenv
```

**`.env` (example):**

```
DEBUG=True
SECRET_KEY=change-me
ALLOWED_HOSTS=*
FIREBASE_CREDENTIALS_PATH=path/to/serviceAccount.json
```

> Add `.env` and `serviceAccount.json` to `.gitignore`.

### 3) Mobile Setup (Kivy)

```bash
cd ../mobile
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**`mobile/requirements.txt` (suggested):**

```
kivy
plyer
requests
firebase-admin
```

---

## 🔌 Minimal API (v1)

The backend provides a thin REST layer; realtime location data can live in Firebase.

**Auth**

* `POST /api/auth/register` — create user (if using Django auth)
* `POST /api/auth/login` — obtain token/session

**Buddies**

* `GET /api/buddies/` — list buddies
* `POST /api/buddies/` — add buddy `{ email }`

**Groups**

* `POST /api/groups/` — create group → returns `code`
* `POST /api/groups/join` — join via `{ code }`
* `POST /api/groups/destination` — leader sets `{ lat, lng, label }`

> For v1, **locations** can be written/read directly from Firebase (`/locations/{userId}`) for simplicity.

---

## 🗺️ Data Model (simple)

**Firestore / Realtime DB**

```
users/{uid}:
  displayName, email
locations/{uid}:
  lat, lng, updatedAt
groups/{groupId}:
  leaderUid, code, destination { lat, lng, label }, members [uid]
```

---

## 🛡️ Environment & Secrets

* `serviceAccount.json` (Firebase Admin) — **do not commit**
* `.env` for Django secrets and Firebase path — **do not commit**

---

## 🧪 Dev Notes

* Start backend first (`http://127.0.0.1:8000/`)
* Point mobile app to backend base URL and Firebase project
* Use mocked GPS if needed while testing

---

## ✅ Roadmap

* [ ] Email/Password auth with Firebase (mobile) or DRF token auth (backend)
* [ ] Location permission + periodic updates with Plyer
* [ ] Map screen with self marker
* [ ] Buddy list + markers
* [ ] Create/join group via code
* [ ] Leader sets destination (visible to all)
* [ ] Basic error states + loading indicators

---

## 🧰 Scripts

Common Git workflow:

```bash
git add .
git commit -m "feat: initial v1 skeleton"
git push origin main
```

---

## 🤝 Contributing

PRs welcome. Please open an issue for feature requests/bugs.



MIT (or your preferred license). Add `LICENSE` file at repo root.


