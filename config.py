import os
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    """Centralized configuration for the Women's Safety and Emergency Assistance System."""

    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-change-this-secret-key-in-production")

    # SQLite Database Configuration
    DATABASE_DIR = os.path.join(BASE_DIR, "database")
    DATABASE_PATH = os.path.join(DATABASE_DIR, "womens_safety.db")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{DATABASE_PATH}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secure Session Configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # Notification Service Configuration
    # Simulation Mode is ON by default during development unless explicitly disabled
    # and valid SMTP or Twilio credentials are provided.
    NOTIFICATION_SIMULATION_MODE = (
        os.environ.get("NOTIFICATION_SIMULATION_MODE", "true").lower() == "true"
    )

    # Optional SMTP Email Configuration
    SMTP_HOST = os.environ.get("SMTP_HOST", "")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    SMTP_USE_TLS = os.environ.get("SMTP_USE_TLS", "true").lower() == "true"
    SMTP_FROM_EMAIL = os.environ.get("SMTP_FROM_EMAIL", "alerts@womens-safety.local")

    # Optional Twilio SMS Configuration
    TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
    TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER", "")

    # Default Seeded Administrator Credentials (override via environment variables in production)
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@womenssafety.in")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@Safe2026!")
    ADMIN_NAME = os.environ.get("ADMIN_NAME", "System Administrator")
    ADMIN_PHONE = os.environ.get("ADMIN_PHONE", "112")
