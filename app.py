import os
from flask import Flask, render_template, session
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, User
from seed import seed_initial_data

csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure database folder exists
    os.makedirs(app.config["DATABASE_DIR"], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.contacts import contacts_bp
    from routes.sos import sos_bp
    from routes.services import services_bp
    from routes.incidents import incidents_bp
    from routes.notifications import notifications_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(sos_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(incidents_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(admin_bp)

    # Inject current_user and simulation flag globally in templates
    @app.context_processor
    def inject_globals():
        current_user = None
        user_id = session.get("user_id")
        if user_id:
            current_user = db.session.get(User, user_id)
        return {
            "current_user": current_user,
            "simulation_mode": app.config.get("NOTIFICATION_SIMULATION_MODE", True),
        }

    # Global error handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("error.html", code=403, title="Access Denied", message="You do not have permission to access this resource."), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("error.html", code=404, title="Page Not Found", message="The requested page could not be found."), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("error.html", code=500, title="Server Error", message="An unexpected error occurred. Please try again."), 500

    with app.app_context():
        db.create_all()
        seed_initial_data()

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
