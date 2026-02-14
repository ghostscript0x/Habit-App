from app.blueprints.auth import auth_bp
from app.blueprints.habits import habits_bp
from app.blueprints.relapse import relapse_bp
from app.blueprints.dashboard import dashboard_bp
from app.blueprints.admin import admin_bp
from app.blueprints.journal import journal_bp
from app.blueprints.mood import mood_bp
from app.blueprints.trigger import trigger_bp
from app.blueprints.achievement import achievement_bp
from app.blueprints.consistency import consistency_bp
from app.blueprints.addiction import addiction_bp
from app.blueprints.export_calendar import export_bp, calendar_bp
from app.blueprints.help import help_bp
from app.blueprints.leaderboard import leaderboard_bp
from app.blueprints.partner import partner_bp
from app.blueprints.landing import landing_bp


def register_blueprints(app):
    app.register_blueprint(landing_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(habits_bp)
    app.register_blueprint(relapse_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(journal_bp)
    app.register_blueprint(mood_bp)
    app.register_blueprint(trigger_bp)
    app.register_blueprint(achievement_bp)
    app.register_blueprint(consistency_bp)
    app.register_blueprint(addiction_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(help_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(partner_bp)
