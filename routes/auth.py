from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from models import db, User
from routes.utils import get_logged_in_user, is_valid_email, is_valid_phone

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if get_logged_in_user():
        return redirect(url_for("dashboard.user_dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = []
        if len(full_name) < 2 or len(full_name) > 120:
            errors.append("Full name must be between 2 and 120 characters.")
        if not is_valid_email(email):
            errors.append("Please enter a valid email address.")
        if not is_valid_phone(phone):
            errors.append("Please enter a valid phone number (7–18 digits).")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if password != confirm_password:
            errors.append("Passwords do not match.")

        if not errors and User.query.filter_by(email=email).first():
            errors.append("An account with this email address already exists.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template(
                "register.html",
                form_data={"full_name": full_name, "email": email, "phone": phone},
            )

        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            role="user",
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in to continue.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form_data={})


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    existing_user = get_logged_in_user()
    if existing_user:
        if existing_user.role == "admin":
            return redirect(url_for("admin.admin_dashboard"))
        return redirect(url_for("dashboard.user_dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("login.html", email=email)

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email address or password.", "danger")
            return render_template("login.html", email=email)

        session.clear()
        session["user_id"] = user.id
        session["user_role"] = user.role
        session.permanent = True

        flash(f"Welcome back, {user.full_name}!", "success")
        if user.role == "admin":
            return redirect(url_for("admin.admin_dashboard"))
        return redirect(url_for("dashboard.user_dashboard"))

    return render_template("login.html", email="")


@auth_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    existing_user = get_logged_in_user()
    if existing_user and existing_user.role == "admin":
        return redirect(url_for("admin.admin_dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email, role="admin").first()
        if not user or not user.check_password(password):
            flash("Invalid administrator credentials.", "danger")
            return render_template("admin_login.html", email=email)

        session.clear()
        session["user_id"] = user.id
        session["user_role"] = "admin"
        session.permanent = True

        flash("Administrator session started.", "success")
        return redirect(url_for("admin.admin_dashboard"))

    return render_template("admin_login.html", email="")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out securely.", "info")
    return redirect(url_for("auth.login"))
