from flask import Blueprint, jsonify, render_template, request
from models import EmergencyService
from routes.utils import haversine_km, login_required, parse_coordinates

services_bp = Blueprint("services", __name__)


@services_bp.route("/services")
@login_required
def nearby_services():
    cities = [
        row[0]
        for row in EmergencyService.query.with_entities(EmergencyService.city)
        .distinct()
        .order_by(EmergencyService.city.asc())
        .all()
    ]
    return render_template("services.html", cities=cities)


@services_bp.route("/api/services")
@login_required
def api_services():
    service_type = request.args.get("type", "").strip().lower()
    city = request.args.get("city", "").strip()
    lat, lng = parse_coordinates(request.args.get("lat"), request.args.get("lng"))

    query = EmergencyService.query
    if service_type in ("police", "hospital"):
        query = query.filter_by(service_type=service_type)
    if city:
        query = query.filter_by(city=city)

    services = query.all()
    results = []
    for svc in services:
        distance_km = None
        if lat is not None and lng is not None:
            distance_km = haversine_km(lat, lng, svc.latitude, svc.longitude)
        results.append(
            {
                "id": svc.id,
                "name": svc.name,
                "service_type": svc.service_type,
                "address": svc.address,
                "phone": svc.phone,
                "city": svc.city,
                "latitude": svc.latitude,
                "longitude": svc.longitude,
                "is_24x7": svc.is_24x7,
                "distance_km": distance_km,
            }
        )

    if lat is not None and lng is not None:
        results.sort(key=lambda item: item["distance_km"] if item["distance_km"] is not None else 999999)

    return jsonify({"services": results, "user_location": {"lat": lat, "lng": lng} if lat is not None else None})
