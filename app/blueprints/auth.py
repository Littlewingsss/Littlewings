from flask import Blueprint, render_template, redirect, request, url_for, flash, Response, current_app, session
from flask_login import login_user, login_required, logout_user
from flask_babel import _
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm

bp = Blueprint('auth', __name__)


@bp.route('/')
def index():
    return render_template('welcome.html')


@bp.route('/home')
@login_required
def home():
    return render_template('home.html')


@bp.route('/logout')
@login_required
def logout() -> Response:
    logout_user()
    flash(_('Je bent nu uitgelogd!'), 'success')
    return redirect(url_for('auth.index'))


@bp.route('/login', methods=['GET', 'POST'])
def login() -> str | Response:
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
        if user is not None and user.check_password(password):
            login_user(user)
            flash(_('Succesvol ingelogd.'), 'success')
            return redirect(url_for('auth.home'))
        flash(_('Verkeerd email of wachtwoord!'), 'danger')
        return redirect(url_for('auth.index'))
    return render_template('login.html', form=LoginForm())


@bp.route('/register', methods=['GET', 'POST'])
def register() -> str | Response:
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        if password != confirm:
            flash(_('Wachtwoorden komen niet overeen!'), 'danger')
            return redirect(url_for('auth.index'))
        bestaande_user = User.query.filter_by(username=username).first()
        bestaande_email = User.query.filter_by(email=email).first()
        if bestaande_user:
            flash(_('Gebruikersnaam is al in gebruik!'), 'danger')
            return redirect(url_for('auth.index'))
        if bestaande_email:
            flash(_('Email is al in gebruik!'), 'danger')
            return redirect(url_for('auth.index'))
        user = User(email=email, username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash(_('Dank voor de registratie. Je kan nu inloggen!'), 'success')
        return redirect(url_for('auth.index'))
    return render_template('register.html', form=RegistrationForm())


@bp.route('/over-ons')
def over_ons():
    return render_template('over_ons.html')


@bp.route('/taal/<lang>')
def set_language(lang):
    if lang in ('nl', 'en'):
        session['lang'] = lang
    return redirect(request.referrer or url_for('auth.index'))


def _maak_reset_token(email: str) -> str:
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(email, salt='wachtwoord-reset')


def _verifieer_reset_token(token: str, max_age: int = 3600) -> str | None:
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        return s.loads(token, salt='wachtwoord-reset', max_age=max_age)
    except (SignatureExpired, BadSignature):
        return None


@bp.route('/wachtwoord-vergeten', methods=['GET', 'POST'])
def wachtwoord_vergeten():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = User.query.filter_by(email=email).first()
        if user:
            from app.mail import stuur_reset_mail
            token = _maak_reset_token(user.email)
            stuur_reset_mail(user, token)
        flash(_('Als er een account bestaat met dit e-mailadres, ontvang je een resetlink.'), 'info')
        return redirect(url_for('auth.index'))
    return render_template('wachtwoord_vergeten.html')


@bp.route('/wachtwoord-reset/<token>', methods=['GET', 'POST'])
def wachtwoord_reset(token):
    email = _verifieer_reset_token(token)
    if not email:
        flash(_('Deze resetlink is ongeldig of verlopen.'), 'danger')
        return redirect(url_for('auth.wachtwoord_vergeten'))
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if len(password) < 6:
            flash(_('Wachtwoord moet minimaal 6 tekens zijn.'), 'danger')
            return redirect(request.url)
        if password != confirm:
            flash(_('Wachtwoorden komen niet overeen.'), 'danger')
            return redirect(request.url)
        user = User.query.filter_by(email=email).first()
        if not user:
            flash(_('Gebruiker niet gevonden.'), 'danger')
            return redirect(url_for('auth.index'))
        user.set_password(password)
        db.session.commit()
        flash(_('Wachtwoord succesvol gewijzigd! Je kan nu inloggen.'), 'success')
        return redirect(url_for('auth.index'))
    return render_template('wachtwoord_reset.html', token=token)
