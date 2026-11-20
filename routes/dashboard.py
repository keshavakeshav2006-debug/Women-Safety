from flask import Blueprint, render_template
from models import EmergencyAlert, EmergencyContact, IncidentReport
from routes.utils import get_logged_in_user, login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def home():
    user = get_logged_in_user()
    return render_template("index.html", user=user)


@dashboard_bp.route("/dashboard")
@login_required
def user_dashboard():
    user = get_logged_in_user()
    contacts = (
        EmergencyContact.query.filter_by(user_id=user.id)
        .order_by(EmergencyContact.created_at.desc())
        .limit(5)
        .all()
    )
    total_contacts = EmergencyContact.query.filter_by(user_id=user.id).count()
    recent_alerts = (
        EmergencyAlert.query.filter_by(user_id=user.id)
        .order_by(EmergencyAlert.created_at.desc())
        .limit(5)
        .all()
    )
    active_alert_count = EmergencyAlert.query.filter_by(
        user_id=user.id, status="active"
    ).count()
    total_reports = IncidentReport.query.filter_by(user_id=user.id).count()

    return render_template(
        "dashboard.html",
        user=user,
        contacts=contacts,
        total_contacts=total_contacts,
        recent_alerts=recent_alerts,
        active_alert_count=active_alert_count,
        total_reports=total_reports,
    )


@dashboard_bp.route("/safety-info")
def safety_info():
    helplines = [
        {"number": "112", "name": "National Emergency Number (India)", "desc": "24/7 unified emergency response for Police, Fire, and Medical assistance."},
        {"number": "1091", "name": "Women Helpline (All India)", "desc": "Dedicated police helpline for women in distress."},
        {"number": "181", "name": "Women Helpline (Domestic Abuse)", "desc": "24/7 support, counseling, and rescue assistance."},
        {"number": "100", "name": "Police Control Room", "desc": "Immediate local police emergency response."},
        {"number": "108", "name": "Emergency Medical / Ambulance", "desc": "24/7 ambulance and medical trauma response."},
        {"number": "1930", "name": "Cyber Crime Helpline", "desc": "Report online harassment, cyberstalking, or digital fraud."},
    ]
    return render_template("safety_info.html", helplines=helplines)
