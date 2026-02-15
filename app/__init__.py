from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache
import redis

from app.config import config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()
cache = Cache()
redis_client = None

login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    cache.init_app(app)

    global redis_client
    redis_client = redis.from_url(
        app.config.get("REDIS_URL", "redis://localhost:6379/0")
    )

    from app.blueprints import register_blueprints

    register_blueprints(app)

    from app.utils.errors import register_error_handlers

    register_error_handlers(app)

    from app import models

    # Initialize social cache on startup
    with app.app_context():
        try:
            from app.services.social_cache_service import initialize_social_cache

            initialize_social_cache()
        except Exception as e:
            print(f"Could not initialize social cache: {e}")

    return app
