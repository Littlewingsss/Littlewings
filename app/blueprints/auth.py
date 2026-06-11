from flask import Blueprint, render_template, redirect, request, url_for, flash, Response
from flask_login import login_user, login_required, logout_user
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
    flash('Je bent nu uitgelogd!', 'success')
    return redirect(url_for('auth.index'))


@bp.route('/login', methods=['GET', 'POST'])
def login() -> str | Response:
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
        if user is not None and user.check_password(password):
            login_user(user)
            flash('Succesvol ingelogd.', 'success')
            return redirect(url_for('auth.home'))
        flash('Verkeerd email of wachtwoord!', 'danger')
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
            flash('Wachtwoorden komen niet overeen!', 'danger')
            return redirect(url_for('auth.index'))
        bestaande_user = User.query.filter_by(username=username).first()
        bestaande_email = User.query.filter_by(email=email).first()
        if bestaande_user:
            flash('Gebruikersnaam is al in gebruik!', 'danger')
            return redirect(url_for('auth.index'))
        if bestaande_email:
            flash('Email is al in gebruik!', 'danger')
            return redirect(url_for('auth.index'))
        user = User(email=email, username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Dank voor de registratie. Je kan nu inloggen!', 'success')
        return redirect(url_for('auth.index'))
    return render_template('register.html', form=RegistrationForm())


@bp.route('/over-ons')
def over_ons():
    return render_template('over_ons.html')
