import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

migrate = Migrate()
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32))
    basedir = os.path.abspath(os.path.dirname(__file__))
    DB_DIR = os.path.join(basedir, '..', 'instance')
    os.makedirs(DB_DIR, exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(DB_DIR, 'db.sqlite')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.index'
    migrate.init_app(app, db)
    csrf.init_app(app)

    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.shop import bp as shop_bp
    from app.blueprints.admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(admin_bp)

    return app
