from app.blueprints.auth import auth_bp
from app.blueprints.habits import habits_bp
from app.blueprints.relapse import relapse_bp
from app.blueprints.dashboard import dashboard_bp
from app.blueprints.admin import admin_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(habits_bp)
    app.register_blueprint(relapse_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
