from flask import current_app
from models import db, User, EmergencyService


SEED_EMERGENCY_SERVICES = [
    # New Delhi
    {
        "name": "Connaught Place Police Station",
        "service_type": "police",
        "address": "Baba Kharak Singh Marg, Connaught Place, New Delhi",
        "phone": "011-23361231",
        "city": "New Delhi",
        "latitude": 28.6315,
        "longitude": 77.2167,
        "is_24x7": True,
    },
    {
        "name": "AIIMS Trauma & Emergency Center",
        "service_type": "hospital",
        "address": "Sri Aurobindo Marg, Ansari Nagar, New Delhi",
        "phone": "011-26588500",
        "city": "New Delhi",
        "latitude": 28.5672,
        "longitude": 77.2100,
        "is_24x7": True,
    },
    {
        "name": "Women's Police Station - Nanakpura",
        "service_type": "police",
        "address": "Nanakpura, Moti Bagh, New Delhi",
        "phone": "011-24673366",
        "city": "New Delhi",
        "latitude": 28.5823,
        "longitude": 77.1704,
        "is_24x7": True,
    },
    {
        "name": "Safdarjung Hospital Emergency",
        "service_type": "hospital",
        "address": "Ansari Nagar West, New Delhi",
        "phone": "011-26707444",
        "city": "New Delhi",
        "latitude": 28.5680,
        "longitude": 77.2060,
        "is_24x7": True,
    },
    # Mumbai
    {
        "name": "Colaba Police Station",
        "service_type": "police",
        "address": "Shahid Bhagat Singh Road, Colaba, Mumbai",
        "phone": "022-22856817",
        "city": "Mumbai",
        "latitude": 18.9151,
        "longitude": 72.8258,
        "is_24x7": True,
    },
    {
        "name": "KEM Hospital Emergency",
        "service_type": "hospital",
        "address": "Acharya Donde Marg, Parel, Mumbai",
        "phone": "022-24107000",
        "city": "Mumbai",
        "latitude": 19.0022,
        "longitude": 72.8415,
        "is_24x7": True,
    },
    {
        "name": "Bandra Police Station",
        "service_type": "police",
        "address": "Hill Road, Bandra West, Mumbai",
        "phone": "022-26423122",
        "city": "Mumbai",
        "latitude": 19.0558,
        "longitude": 72.8332,
        "is_24x7": True,
    },
    # Bengaluru
    {
        "name": "Cubbon Park Police Station",
        "service_type": "police",
        "address": "Kasturba Road, Sampangi Rama Nagar, Bengaluru",
        "phone": "080-22942546",
        "city": "Bengaluru",
        "latitude": 12.9763,
        "longitude": 77.5929,
        "is_24x7": True,
    },
    {
        "name": "St. Martha's Hospital Emergency",
        "service_type": "hospital",
        "address": "Nrupathunga Road, Sampangi Rama Nagar, Bengaluru",
        "phone": "080-22275081",
        "city": "Bengaluru",
        "latitude": 12.9724,
        "longitude": 77.5861,
        "is_24x7": True,
    },
    {
        "name": "Indiranagar Police Station",
        "service_type": "police",
        "address": "100 Feet Road, Indiranagar, Bengaluru",
        "phone": "080-22942530",
        "city": "Bengaluru",
        "latitude": 12.9784,
        "longitude": 77.6408,
        "is_24x7": True,
    },
    # Chennai & Hyderabad
    {
        "name": "All Women Police Station - Thousand Lights",
        "service_type": "police",
        "address": "Greams Road, Thousand Lights, Chennai",
        "phone": "044-28290323",
        "city": "Chennai",
        "latitude": 13.0604,
        "longitude": 80.2548,
        "is_24x7": True,
    },
    {
        "name": "Apollo Hospitals Emergency - Greams Road",
        "service_type": "hospital",
        "address": "21 Greams Lane, Off Greams Road, Chennai",
        "phone": "044-28293333",
        "city": "Chennai",
        "latitude": 13.0632,
        "longitude": 80.2516,
        "is_24x7": True,
    },
    {
        "name": "Banjara Hills Police Station",
        "service_type": "police",
        "address": "Road No. 12, Banjara Hills, Hyderabad",
        "phone": "040-27853540",
        "city": "Hyderabad",
        "latitude": 17.4126,
        "longitude": 78.4401,
        "is_24x7": True,
    },
    {
        "name": "NIMS Hospital Emergency",
        "service_type": "hospital",
        "address": "Punjagutta, Hyderabad",
        "phone": "040-23489000",
        "city": "Hyderabad",
        "latitude": 17.4227,
        "longitude": 78.4521,
        "is_24x7": True,
    },
]


def seed_initial_data() -> None:
    """Create default admin account and emergency services if they do not exist."""
    admin_email = current_app.config["ADMIN_EMAIL"].lower()
    existing_admin = User.query.filter_by(email=admin_email).first()
    if not existing_admin:
        admin_user = User(
            full_name=current_app.config["ADMIN_NAME"],
            email=admin_email,
            phone=current_app.config["ADMIN_PHONE"],
            role="admin",
        )
        admin_user.set_password(current_app.config["ADMIN_PASSWORD"])
        db.session.add(admin_user)

    if EmergencyService.query.count() == 0:
        for item in SEED_EMERGENCY_SERVICES:
            db.session.add(EmergencyService(**item))

    db.session.commit()
