from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def utc_now():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    # Relationships
    contacts = db.relationship(
        "EmergencyContact",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    alerts = db.relationship(
        "EmergencyAlert",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    incident_reports = db.relationship(
        "IncidentReport",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    def masked_phone(self) -> str:
        if not self.phone or len(self.phone) < 4:
            return "****"
        return "*" * (len(self.phone) - 4) + self.phone[-4:]

    def masked_email(self) -> str:
        if "@" not in self.email:
            return "***"
        local, domain = self.email.split("@", 1)
        prefix = local[:2] if len(local) >= 2 else local[:1]
        return f"{prefix}***@{domain}"


class EmergencyContact(db.Model):
    __tablename__ = "emergency_contacts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    relationship = db.Column(db.String(60), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    user = db.relationship("User", back_populates="contacts")
    notifications = db.relationship(
        "Notification",
        back_populates="contact",
        cascade="all, delete-orphan",
    )


class EmergencyAlert(db.Model):
    __tablename__ = "emergency_alerts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    accuracy_meters = db.Column(db.Float, nullable=True)
    map_link = db.Column(db.String(300), nullable=True)
    location_status = db.Column(db.String(50), nullable=False, default="not_shared")  # captured, denied, unavailable, not_shared
    message = db.Column(db.String(300), nullable=False, default="SOS! I need immediate emergency assistance.")
    status = db.Column(db.String(30), nullable=False, default="active")  # active, resolved, cancelled
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now, index=True)
    resolved_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="alerts")
    notifications = db.relationship(
        "Notification",
        back_populates="alert",
        cascade="all, delete-orphan",
        lazy="select",
    )


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey("emergency_alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id = db.Column(db.Integer, db.ForeignKey("emergency_contacts.id", ondelete="SET NULL"), nullable=True)
    contact_name = db.Column(db.String(120), nullable=False)
    recipient = db.Column(db.String(150), nullable=False)
    channel = db.Column(db.String(20), nullable=False)  # sms, email, simulation
    status = db.Column(db.String(30), nullable=False, default="pending")  # pending, sent, simulated, failed
    mode = db.Column(db.String(20), nullable=False, default="simulation")  # simulation, live
    provider_message = db.Column(db.String(300), nullable=True)
    sent_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    alert = db.relationship("EmergencyAlert", back_populates="notifications")
    contact = db.relationship("EmergencyContact", back_populates="notifications")


class IncidentReport(db.Model):
    __tablename__ = "incident_reports"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)
    incident_date = db.Column(db.Date, nullable=False)
    location_text = db.Column(db.String(250), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(30), nullable=False, default="submitted")  # submitted, under_review, resolved
    admin_note = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now, index=True)

    user = db.relationship("User", back_populates="incident_reports")


class EmergencyService(db.Model):
    __tablename__ = "emergency_services"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    service_type = db.Column(db.String(30), nullable=False, index=True)  # police, hospital
    address = db.Column(db.String(250), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    city = db.Column(db.String(80), nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    is_24x7 = db.Column(db.Boolean, nullable=False, default=True)
