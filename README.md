# Women's Safety and Emergency Assistance System

A complete, database-connected web application built with **Python (Flask)**, **SQLite (SQLAlchemy ORM)**, **HTML5/CSS3/JavaScript**, **Bootstrap 5**, and **Leaflet.js + OpenStreetMap**.

## Technology Stack

- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons
- **Backend:** Python 3.10+, Flask 3.1, Flask-SQLAlchemy, Flask-WTF (CSRF)
- **Database:** SQLite (`database/womens_safety.db`)
- **Maps & Location:** OpenStreetMap, Leaflet.js 1.9, Browser Geolocation API

## Implemented Modules (1–11)

1. **User Registration & Login (`routes/auth.py`)** — Password hashing (`werkzeug.security`), input validation, secure session cookies, logout.
2. **User Dashboard (`routes/dashboard.py`)** — Welcome banner, emergency assistance options, saved contacts preview, recent SOS alerts, quick links.
3. **Emergency Contact Management (`routes/contacts.py`)** — Add, edit, delete, and list trusted contacts scoped to the logged-in user.
4. **SOS Emergency Alert (`routes/sos.py`, `static/js/sos.js`)** — Large pulsing SOS button, confirmation modal, optional permission-based GPS capture, India `tel:112` call option, contact notification dispatch.
5. **Live Location Sharing (`routes/sos.py`, `static/js/map.js`, `static/js/geolocation.js`)** — Explicit location permission prompt, live lat/lng/accuracy readout, Leaflet + OpenStreetMap view, shareable map link, and Stop Sharing button.
6. **Nearby Emergency Services (`routes/services.py`, `static/js/map.js`)** — Seeded police stations and hospitals plotted on Leaflet + OpenStreetMap with city/type filters and Haversine distance sorting.
7. **Incident Reporting (`routes/incidents.py`)** — Submit safety incident reports (category, description, date, location text, optional GPS) and view report status.
8. **Emergency Notifications (`routes/notifications.py`)** — Supports SMTP Email & Twilio SMS when configured; runs in clearly labelled **Simulation Mode** during development (never falsely marking unconfirmed alerts as delivered).
9. **SOS History (`routes/sos.py`)** — View past alerts, timestamps, shared map links, alert status controls, and per-contact notification logs.
10. **Admin Dashboard (`routes/admin.py`)** — Role-protected admin login and dashboard with statistics, incident review/status updates, alert resolution, and masked user PII.
11. **Safety Information (`routes/dashboard.py`)** — India emergency helplines (`112`, `1091`, `181`, `100`, `108`, `1930`), direct calling links, and safety guidelines.

## Project Structure

```text
.
├── app.py                  # Flask app factory, CSRF, Blueprints, DB creation & seeding
├── config.py               # Database, session security, notification & admin config
├── models.py               # 6 SQLAlchemy ORM tables with foreign key relationships
├── seed.py                 # Seeds admin user and nearby emergency services
├── requirements.txt        # Python package dependencies
├── .env.flask.example      # Example Flask environment variables
├── database/               # SQLite database directory (womens_safety.db)
├── routes/
│   ├── __init__.py
│   ├── utils.py            # Auth decorators, validators, Haversine & OSM helpers
│   ├── auth.py
│   ├── dashboard.py
│   ├── contacts.py
│   ├── sos.py
│   ├── services.py
│   ├── incidents.py
│   ├── notifications.py
│   └── admin.py
├── templates/              # Jinja2 HTML5 + Bootstrap 5 templates
├── static/
│   ├── css/style.css
│   └── js/
│       ├── main.js
│       ├── geolocation.js
│       ├── sos.js
│       └── map.js
└── tests/
    └── test_app.py         # Automated unittest suite
```

## Running Locally (VS Code / Terminal)

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # Windows: venv\Scripts\activate
   # macOS/Linux: source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Copy `.env.flask.example` to `.env` and update secrets or SMTP/Twilio keys.
4. Start the Flask server:
   ```bash
   python app.py
   ```
5. Open `http://127.0.0.1:5000` in your browser.
   - **Default Admin Login (`/admin/login`):** `admin@womenssafety.in` / `Admin@Safe2026!` (change in production via environment variables).

## Running Automated Tests

```bash
python -m unittest discover -s tests -v
```
