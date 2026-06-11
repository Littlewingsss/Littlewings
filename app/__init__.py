import os
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_babel import Babel, get_locale

migrate = Migrate()
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()
babel = Babel()


def _get_locale():
    return session.get('lang', 'nl')

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

    app.config['BABEL_DEFAULT_LOCALE'] = 'nl'
    app.config['BABEL_SUPPORTED_LOCALES'] = ['nl', 'en']

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.index'
    migrate.init_app(app, db)
    csrf.init_app(app)
    mail.init_app(app)
    babel.init_app(app, locale_selector=_get_locale)

    app.jinja_env.globals['get_locale'] = _get_locale

    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.shop import bp as shop_bp
    from app.blueprints.admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(admin_bp)

    from flask import render_template

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app
