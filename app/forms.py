from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Wachtwoord'), validators=[DataRequired()])
    submit = SubmitField(_l('Inloggen'))


class RegistrationForm(FlaskForm):
    username = StringField(_l('Gebruikersnaam'), validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Wachtwoord'), validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(_l('Bevestig wachtwoord'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Registreren'))
