# from flask import Flask
# from celery import Celery
# app = Flask(__name__)
# celery = Celery(
#     __name__,
#     broker="redis://127.0.0.1:6379/0",
#     backend="redis://127.0.0.1:6379/0"
# )
# @app.route("/")
# def hello():
#     return "Hello, World!"
# @celery.task
# def divide(x, y):
#     import time
#     time.sleep(5)
#     return x / y

import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from project.config import config

db=SQLAlchemy()
migrate=Migrate()
def create_app():
    if config_name is None:
            config_name = os.environ.get("FLASK_CONFIG", "development")
    app=Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    migrate.init_app(app)
    from project.users import users_blueprint
    app.register_blueprint(users_blueprint)
    @app.shell_context_processor
    def ctx():
        return {"app":app, "db":db}
    return app