import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from .config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    basedir = os.path.abspath(os.path.dirname(__file__))
    load_dotenv(os.path.join(basedir, '..', '.env'), encoding='utf-8')

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import bp
    app.register_blueprint(bp)

    return app
