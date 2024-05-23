import atexit
from flask import Flask
from flask import url_for
from flask_migrate import Migrate
from .models import db
# from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy()


# end of impor
# 6. part of jojo bizarre adventure iss the becst
def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    print(app.config)
    db.init_app(app)
    Migrate(app, db)

    from .views import api_bp

    app.register_blueprint(api_bp, url_prefix="/api")
    from .tasks import start_scheduler, stop_scheduler

    stop_scheduler()
    start_scheduler()
    atexit.register(stop_scheduler)

    @app.route("/site-map")
    def site_map():
        links = []
        for rule in app.url_map.iter_rules():
            # Filter out rules we can't navigate to in a browser
            # and rules that require parameters
            if "GET" in rule.methods and has_no_empty_params(rule):
                url = url_for(rule.endpoint, **(rule.defaults or {}))
                links.append((url, rule.endpoint))
        # links is now a list of url, endpoint tuples

    @app.route("/ping", methods=["GET"])
    def ping():
        return "pong"

    return app


app = create_app()
