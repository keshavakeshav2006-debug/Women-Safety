import smtplib
from email.message import EmailMessage
import requests
from flask import Blueprint, current_app, render_template
from models import db, EmergencyAlert, Notification
from routes.utils import get_logged_in_user, login_required

notifications_bp = Blueprint("notifications", __name__)


def _send_email(to_email: str, subject: str, body: str) -> tuple[bool, str]:
    host = current_app.config.get("SMTP_HOST", "")
    username = current_app.config.get("SMTP_USERNAME", "")
    password = current_app.config.get("SMTP_PASSWORD", "")
    port = current_app.config.get("SMTP_PORT", 587)
    use_tls = current_app.config.get("SMTP_USE_TLS", True)
    from_email = current_app.config.get("SMTP_FROM_EMAIL", "alerts@womens-safety.local")

    if not host or not username or not password:
        return False, "SMTP email provider is not configured."

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email
        msg.set_content(body)

        with smtplib.SMTP(host, port, timeout=10) as server:
            if use_tls:
                server.starttls()
            server.login(username, password)
            server.send_message(msg)
        return True, "Accepted by SMTP server."
    except Exception as exc:
        return False, f"SMTP error: {str(exc)[:180]}"


def _send_twilio_sms(to_phone: str, body: str) -> tuple[bool, str]:
    sid = current_app.config.get("TWILIO_ACCOUNT_SID", "")
    token = current_app.config.get("TWILIO_AUTH_TOKEN", "")
    from_number = current_app.config.get("TWILIO_FROM_NUMBER", "")

    if not sid or not token or not from_number:
        return False, "SMS provider (Twilio) is not configured."

    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
        resp = requests.post(
            url,
            data={"From": from_number, "To": to_phone, "Body": body},
            auth=(sid, token),
            timeout=10,
        )
        if resp.status_code in (200, 201):
            return True, "Accepted by SMS gateway."
        return False, f"SMS gateway returned HTTP {resp.status_code}."
    except Exception as exc:
        return False, f"SMS request error: {str(exc)[:180]}"


def dispatch_sos_notifications(alert: EmergencyAlert, user, contacts: list) -> list[Notification]:
    """
    Dispatch notifications to selected trusted contacts.
    In Simulation Mode, marks records explicitly as 'simulated' — never falsely 'sent'.
    In Live Mode, marks 'sent' ONLY when external SMTP/SMS provider confirms acceptance.
    """
    simulation_mode = current_app.config.get("NOTIFICATION_SIMULATION_MODE", True)
    location_part = (
        f"Live Location: {alert.map_link} (Lat: {alert.latitude}, Lng: {alert.longitude})"
        if alert.map_link
        else "Location: Not shared / unavailable at time of alert."
    )
    body = (
        f"EMERGENCY SOS ALERT from {user.full_name} ({user.phone}).\n"
        f"Message: {alert.message}\n"
        f"{location_part}\n"
        f"If unreachable, please call India Emergency Helpline 112 immediately."
    )
    subject = f"URGENT SOS ALERT: {user.full_name} needs help"

    created_notifications = []

    for contact in contacts:
        if simulation_mode:
            notif = Notification(
                alert_id=alert.id,
                contact_id=contact.id,
                contact_name=contact.name,
                recipient=contact.phone,
                channel="simulation",
                status="simulated",
                mode="simulation",
                provider_message=(
                    "Simulation Mode active: Alert logged for verification. "
                    "No real SMS/Email was dispatched."
                ),
            )
            db.session.add(notif)
            created_notifications.append(notif)
            continue

        # Live Mode: try SMS first, and Email if contact has an email address
        sms_ok, sms_msg = _send_twilio_sms(contact.phone, body)
        sms_notif = Notification(
            alert_id=alert.id,
            contact_id=contact.id,
            contact_name=contact.name,
            recipient=contact.phone,
            channel="sms",
            status="sent" if sms_ok else "failed",
            mode="live",
            provider_message=sms_msg,
        )
        db.session.add(sms_notif)
        created_notifications.append(sms_notif)

        if contact.email:
            email_ok, email_msg = _send_email(contact.email, subject, body)
            email_notif = Notification(
                alert_id=alert.id,
                contact_id=contact.id,
                contact_name=contact.name,
                recipient=contact.email,
                channel="email",
                status="sent" if email_ok else "failed",
                mode="live",
                provider_message=email_msg,
            )
            db.session.add(email_notif)
            created_notifications.append(email_notif)

    db.session.commit()
    return created_notifications


@notifications_bp.route("/notifications")
@login_required
def notification_logs():
    user = get_logged_in_user()
    alerts = (
        EmergencyAlert.query.filter_by(user_id=user.id)
        .order_by(EmergencyAlert.created_at.desc())
        .all()
    )
    alert_ids = [a.id for a in alerts]
    logs = []
    if alert_ids:
        logs = (
            Notification.query.filter(Notification.alert_id.in_(alert_ids))
            .order_by(Notification.sent_at.desc())
            .all()
        )
    return render_template("notifications.html", logs=logs)
