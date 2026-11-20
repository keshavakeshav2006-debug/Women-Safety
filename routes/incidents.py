from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from models import db, IncidentReport
from routes.utils import get_logged_in_user, login_required, parse_coordinates

incidents_bp = Blueprint("incidents", __name__)

INCIDENT_CATEGORIES = [
    "Harassment / Eve Teasing",
    "Stalking",
    "Unsafe / Poorly Lit Area",
    "Suspicious Activity",
    "Public Transport Safety",
    "Domestic / Workplace Threat",
    "Cyber Harassment",
    "Other Safety Concern",
]


@incidents_bp.route("/incidents", methods=["GET", "POST"])
@login_required
def manage_incidents():
    user = get_logged_in_user()

    if request.method == "POST":
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        date_str = request.form.get("incident_date", "").strip()
        location_text = request.form.get("location_text", "").strip()
        lat, lng = parse_coordinates(
            request.form.get("latitude"), request.form.get("longitude")
        )

        errors = []
        if category not in INCIDENT_CATEGORIES:
            errors.append("Please select a valid incident category.")
        if len(description) < 10 or len(description) > 2000:
            errors.append("Description must be between 10 and 2000 characters.")
        if len(location_text) < 3 or len(location_text) > 250:
            errors.append("Please provide a valid location description.")

        parsed_date = None
        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            errors.append("Please enter a valid incident date (YYYY-MM-DD).")

        if errors:
            for err in errors:
                flash(err, "danger")
        else:
            report = IncidentReport(
                user_id=user.id,
                category=category,
                description=description,
                incident_date=parsed_date,
                location_text=location_text,
                latitude=lat,
                longitude=lng,
                status="submitted",
            )
            db.session.add(report)
            db.session.commit()
            flash("Incident report submitted safely and stored in our records.", "success")
            return redirect(url_for("incidents.manage_incidents"))

    reports = (
        IncidentReport.query.filter_by(user_id=user.id)
        .order_by(IncidentReport.created_at.desc())
        .all()
    )
    return render_template(
        "incidents.html",
        categories=INCIDENT_CATEGORIES,
        reports=reports,
    )
