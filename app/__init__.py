from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import atexit

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate = Migrate(app, db)

    from .views import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from .tasks import start_scheduler, stop_scheduler
    start_scheduler()
    atexit.register(stop_scheduler)

    return app
