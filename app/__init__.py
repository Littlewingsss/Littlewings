import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail

migrate = Migrate()
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32))
    basedir = os.path.abspath(os.path.dirname(__file__))
    DB_DIR = os.path.join(basedir, '..', 'instance')
    os.makedirs(DB_DIR, exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(DB_DIR, 'db.sqlite')

    app.config['MAIL_SERVER']         = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT']           = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS']        = True
    app.config['MAIL_USERNAME']       = os.environ.get('MAIL_USERNAME') or None
    app.config['MAIL_PASSWORD']       = os.environ.get('MAIL_PASSWORD') or None
    app.config['MAIL_DEFAULT_SENDER'] = (
        os.environ.get('MAIL_DEFAULT_SENDER') or os.environ.get('MAIL_USERNAME') or None
    )

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.index'
    migrate.init_app(app, db)
    csrf.init_app(app)
    mail.init_app(app)

    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.shop import bp as shop_bp
    from app.blueprints.admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(admin_bp)

    return app
