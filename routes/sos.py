from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from models import db, EmergencyAlert, EmergencyContact, utc_now
from routes.notifications import dispatch_sos_notifications
from routes.utils import build_osm_map_link, get_logged_in_user, login_required, parse_coordinates

sos_bp = Blueprint("sos", __name__)


@sos_bp.route("/sos")
@login_required
def sos_page():
    user = get_logged_in_user()
    contacts = (
        EmergencyContact.query.filter_by(user_id=user.id)
        .order_by(EmergencyContact.created_at.desc())
        .all()
    )
    active_alerts = (
        EmergencyAlert.query.filter_by(user_id=user.id, status="active")
        .order_by(EmergencyAlert.created_at.desc())
        .all()
    )
    return render_template("sos.html", contacts=contacts, active_alerts=active_alerts)


@sos_bp.route("/api/sos", methods=["POST"])
@login_required
def trigger_sos():
    user = get_logged_in_user()
    payload = request.get_json(silent=True) or {}

    lat, lng = parse_coordinates(payload.get("latitude"), payload.get("longitude"))
    accuracy = payload.get("accuracy")
    try:
        accuracy_val = round(float(accuracy), 1) if accuracy is not None else None
    except (TypeError, ValueError):
        accuracy_val = None

    location_status = payload.get("location_status", "not_shared")
    if location_status not in ("captured", "denied", "unavailable", "not_shared"):
        location_status = "not_shared"

    if lat is not None and lng is not None:
        map_link = build_osm_map_link(lat, lng)
        location_status = "captured"
    else:
        map_link = None

    raw_message = (payload.get("message") or "").strip()
    message = raw_message[:300] if raw_message else "SOS! I need immediate emergency assistance."

    # Determine selected contacts (owned strictly by this user)
    requested_ids = payload.get("contact_ids")
    user_contacts = EmergencyContact.query.filter_by(user_id=user.id).all()
    if isinstance(requested_ids, list) and requested_ids:
        valid_ids = set()
        for cid in requested_ids:
            try:
                valid_ids.add(int(cid))
            except (TypeError, ValueError):
                continue
        selected_contacts = [c for c in user_contacts if c.id in valid_ids]
    else:
        selected_contacts = user_contacts

    alert = EmergencyAlert(
        user_id=user.id,
        latitude=lat,
        longitude=lng,
        accuracy_meters=accuracy_val,
        map_link=map_link,
        location_status=location_status,
        message=message,
        status="active",
    )
    db.session.add(alert)
    db.session.commit()

    notifications = dispatch_sos_notifications(alert, user, selected_contacts)

    return jsonify(
        {
            "success": True,
            "alert": {
                "id": alert.id,
                "status": alert.status,
                "latitude": alert.latitude,
                "longitude": alert.longitude,
                "map_link": alert.map_link,
                "location_status": alert.location_status,
                "message": alert.message,
                "created_at": alert.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
            },
            "notifications": [
                {
                    "contact_name": n.contact_name,
                    "recipient": n.recipient,
                    "channel": n.channel,
                    "status": n.status,
                    "mode": n.mode,
                    "provider_message": n.provider_message,
                }
                for n in notifications
            ],
            "contact_count": len(selected_contacts),
        }
    ), 201


@sos_bp.route("/sos/<int:alert_id>/status", methods=["POST"])
@login_required
def update_alert_status(alert_id):
    user = get_logged_in_user()
    alert = EmergencyAlert.query.filter_by(id=alert_id, user_id=user.id).first_or_404()
    new_status = request.form.get("status", "").strip().lower()
    if new_status not in ("resolved", "cancelled"):
        flash("Invalid alert status requested.", "danger")
        return redirect(url_for("sos.sos_history"))

    alert.status = new_status
    alert.resolved_at = utc_now()
    db.session.commit()
    flash(f"SOS Alert #{alert.id} marked as {new_status}.", "success")

    next_url = request.form.get("next") or url_for("sos.sos_history")
    return redirect(next_url)


@sos_bp.route("/sos/history")
@login_required
def sos_history():
    user = get_logged_in_user()
    alerts = (
        EmergencyAlert.query.filter_by(user_id=user.id)
        .order_by(EmergencyAlert.created_at.desc())
        .all()
    )
    return render_template("sos_history.html", alerts=alerts)


@sos_bp.route("/location")
@login_required
def location_sharing():
    user = get_logged_in_user()
    contacts = EmergencyContact.query.filter_by(user_id=user.id).all()
    return render_template("location.html", contacts=contacts)
