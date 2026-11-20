from flask import Blueprint, flash, redirect, render_template, request, url_for
from models import db, EmergencyAlert, IncidentReport, Notification, User, utc_now
from routes.utils import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@admin_required
def admin_dashboard():
    total_users = User.query.filter_by(role="user").count()
    total_alerts = EmergencyAlert.query.count()
    active_alerts_count = EmergencyAlert.query.filter_by(status="active").count()
    total_reports = IncidentReport.query.count()
    pending_reports_count = IncidentReport.query.filter(
        IncidentReport.status.in_(["submitted", "under_review"])
    ).count()
    total_notifications = Notification.query.count()

    status_filter = request.args.get("report_status", "").strip().lower()
    reports_query = IncidentReport.query
    if status_filter in ("submitted", "under_review", "resolved"):
        reports_query = reports_query.filter_by(status=status_filter)

    incident_reports = reports_query.order_by(IncidentReport.created_at.desc()).limit(50).all()
    recent_alerts = (
        EmergencyAlert.query.order_by(EmergencyAlert.created_at.desc()).limit(30).all()
    )

    return render_template(
        "admin_dashboard.html",
        stats={
            "total_users": total_users,
            "total_alerts": total_alerts,
            "active_alerts": active_alerts_count,
            "total_reports": total_reports,
            "pending_reports": pending_reports_count,
            "total_notifications": total_notifications,
        },
        incident_reports=incident_reports,
        recent_alerts=recent_alerts,
        status_filter=status_filter,
    )


@admin_bp.route("/incidents/<int:report_id>/update", methods=["POST"])
@admin_required
def update_incident(report_id):
    report = db.session.get(IncidentReport, report_id)
    if not report:
        flash("Incident report not found.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    new_status = request.form.get("status", "").strip().lower()
    admin_note = request.form.get("admin_note", "").strip()[:300]

    if new_status not in ("submitted", "under_review", "resolved"):
        flash("Invalid status value.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    report.status = new_status
    if admin_note:
        report.admin_note = admin_note
    db.session.commit()
    flash(f"Incident Report #{report.id} updated to '{new_status}'.", "success")
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/alerts/<int:alert_id>/resolve", methods=["POST"])
@admin_required
def resolve_alert(alert_id):
    alert = db.session.get(EmergencyAlert, alert_id)
    if not alert:
        flash("Alert not found.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    alert.status = "resolved"
    alert.resolved_at = utc_now()
    db.session.commit()
    flash(f"Emergency Alert #{alert.id} marked as resolved.", "success")
    return redirect(url_for("admin.admin_dashboard"))
