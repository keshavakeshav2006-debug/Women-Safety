import math
import re
from functools import wraps
from flask import abort, flash, redirect, session, url_for
from models import db, User

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_REGEX = re.compile(r"^\+?[0-9\s\-]{7,18}$")


def get_logged_in_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        user = get_logged_in_user()
        if not user:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapped_view


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        user = get_logged_in_user()
        if not user:
            flash("Administrator login is required.", "warning")
            return redirect(url_for("auth.admin_login"))
        if user.role != "admin":
            abort(403)
        return view_func(*args, **kwargs)

    return wrapped_view


def is_valid_email(email: str) -> bool:
    return bool(email and len(email) <= 150 and EMAIL_REGEX.match(email.strip()))


def is_valid_phone(phone: str) -> bool:
    return bool(phone and PHONE_REGEX.match(phone.strip()))


def parse_coordinates(lat_raw, lng_raw):
    """Safely parse and bound-check latitude and longitude values."""
    if lat_raw is None or lng_raw is None or lat_raw == "" or lng_raw == "":
        return None, None
    try:
        lat = float(lat_raw)
        lng = float(lng_raw)
    except (TypeError, ValueError):
        return None, None
    if -90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0:
        return round(lat, 6), round(lng, 6)
    return None, None


def build_osm_map_link(lat: float, lng: float) -> str:
    return f"https://www.openstreetmap.org/?mlat={lat:.6f}&mlon={lng:.6f}#map=17/{lat:.6f}/{lng:.6f}"


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two coordinates in kilometers."""
    r = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return round(2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 2)
