from flask import Blueprint, flash, redirect, render_template, request, url_for
from models import db, EmergencyContact
from routes.utils import get_logged_in_user, is_valid_email, is_valid_phone, login_required

contacts_bp = Blueprint("contacts", __name__)

ALLOWED_RELATIONSHIPS = [
    "Parent",
    "Sibling",
    "Spouse / Partner",
    "Friend",
    "Colleague",
    "Relative",
    "Guardian",
    "Other",
]


@contacts_bp.route("/contacts")
@login_required
def list_contacts():
    user = get_logged_in_user()
    contacts = (
        EmergencyContact.query.filter_by(user_id=user.id)
        .order_by(EmergencyContact.created_at.desc())
        .all()
    )
    return render_template(
        "contacts.html",
        contacts=contacts,
        relationships=ALLOWED_RELATIONSHIPS,
    )


@contacts_bp.route("/contacts/add", methods=["POST"])
@login_required
def add_contact():
    user = get_logged_in_user()
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip().lower()
    relationship = request.form.get("relationship", "").strip()

    errors = []
    if len(name) < 2 or len(name) > 120:
        errors.append("Contact name must be between 2 and 120 characters.")
    if not is_valid_phone(phone):
        errors.append("Please enter a valid contact phone number.")
    if email and not is_valid_email(email):
        errors.append("Please enter a valid email address or leave it blank.")
    if relationship not in ALLOWED_RELATIONSHIPS:
        errors.append("Please select a valid relationship.")

    if errors:
        for err in errors:
            flash(err, "danger")
        return redirect(url_for("contacts.list_contacts"))

    contact = EmergencyContact(
        user_id=user.id,
        name=name,
        phone=phone,
        email=email or None,
        relationship=relationship,
    )
    db.session.add(contact)
    db.session.commit()
    flash(f"Trusted contact '{name}' added successfully.", "success")
    return redirect(url_for("contacts.list_contacts"))


@contacts_bp.route("/contacts/<int:contact_id>/edit", methods=["POST"])
@login_required
def edit_contact(contact_id):
    user = get_logged_in_user()
    contact = EmergencyContact.query.filter_by(id=contact_id, user_id=user.id).first_or_404()

    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip().lower()
    relationship = request.form.get("relationship", "").strip()

    if len(name) < 2 or len(name) > 120 or not is_valid_phone(phone):
        flash("Please provide a valid name and phone number.", "danger")
        return redirect(url_for("contacts.list_contacts"))
    if email and not is_valid_email(email):
        flash("Please provide a valid email address.", "danger")
        return redirect(url_for("contacts.list_contacts"))
    if relationship not in ALLOWED_RELATIONSHIPS:
        flash("Invalid relationship selected.", "danger")
        return redirect(url_for("contacts.list_contacts"))

    contact.name = name
    contact.phone = phone
    contact.email = email or None
    contact.relationship = relationship
    db.session.commit()
    flash(f"Contact '{name}' updated.", "success")
    return redirect(url_for("contacts.list_contacts"))


@contacts_bp.route("/contacts/<int:contact_id>/delete", methods=["POST"])
@login_required
def delete_contact(contact_id):
    user = get_logged_in_user()
    contact = EmergencyContact.query.filter_by(id=contact_id, user_id=user.id).first_or_404()
    contact_name = contact.name
    db.session.delete(contact)
    db.session.commit()
    flash(f"Contact '{contact_name}' removed.", "info")
    return redirect(url_for("contacts.list_contacts"))
