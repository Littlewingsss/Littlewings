from functools import wraps
from flask import abort, redirect, url_for
from flask_login import current_user

ADMIN_EMAILS = ["mr.al.domni@st.hanze.nl", "yahia_hani@outlook.com"]

def admin_required(functie):
    @wraps(functie)
    def check(**url_waarde):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if current_user.email not in ADMIN_EMAILS:
            abort(403)
        return functie(**url_waarde)
    return check