import re
from flask import Blueprint, render_template, redirect, request, url_for, flash, Response, session, abort
from app import db
from app.models import Product, Order, OrderRegel

bp = Blueprint('shop', __name__)


@bp.route('/shop')
def shop():
    producten = Product.query.all()
    return render_template('shop.html', producten=producten)


@bp.route('/toevoegen/<int:product_id>', methods=['POST'])
def toevoegen(product_id):
    product = db.session.get(Product, product_id) or abort(404)
    winkelwagen = session.get('winkelwagen', {})
    key = str(product_id)
    huidige_aantal = winkelwagen.get(key, 0)
    if huidige_aantal >= product.voorraad:
        flash(f'Niet genoeg voorraad! Er zijn nog maar {product.voorraad} stuks beschikbaar.', 'danger')
        return redirect(url_for('shop.shop'))
    winkelwagen[key] = huidige_aantal + 1
    session['winkelwagen'] = winkelwagen
    flash('Product toegevoegd aan je winkelwagen! 🛒', 'success')
    return redirect(url_for('shop.shop'))


@bp.route('/verhogen/<int:product_id>', methods=['POST'])
def verhogen(product_id):
    product = db.session.get(Product, product_id) or abort(404)
    winkelwagen = session.get('winkelwagen', {})
    key = str(product_id)
    huidige_aantal = winkelwagen.get(key, 0)
    if huidige_aantal >= product.voorraad:
        flash(f'Niet genoeg voorraad! Er zijn nog maar {product.voorraad} stuks beschikbaar.', 'danger')
    else:
        winkelwagen[key] = huidige_aantal + 1
        session['winkelwagen'] = winkelwagen
    return redirect(url_for('shop.winkelwagen'))


@bp.route('/verminderen/<int:product_id>', methods=['POST'])
def verminderen(product_id):
    winkelwagen = session.get('winkelwagen', {})
    key = str(product_id)
    if key in winkelwagen:
        winkelwagen[key] -= 1
        if winkelwagen[key] <= 0:
            winkelwagen.pop(key)
    session['winkelwagen'] = winkelwagen
    return redirect(url_for('shop.winkelwagen'))


@bp.route('/winkelwagen', methods=['GET', 'POST'])
def winkelwagen():
    if request.method == 'POST':
        session['verzending'] = request.form.get('verzending', '')
    wagen = session.get('winkelwagen', {})
    gekozen_verzending = session.get('verzending', '')
    items = []
    totaal = 0
    for product_id, aantal in wagen.items():
        product = db.session.get(Product, int(product_id))
        if product:
            subtotaal = product.prijs * aantal
            totaal += subtotaal
            items.append({'product': product, 'aantal': aantal, 'subtotaal': subtotaal})
    verzend_kosten = 4.99 if gekozen_verzending == 'express' else 0.0
    verzend_str = '€ 4,99' if gekozen_verzending == 'express' else ('Gratis' if gekozen_verzending else '—')
    totaal_incl = totaal + verzend_kosten
    return render_template('winkelwagen.html',
        items=items,
        totaal_str="%.2f" % totaal,
        totaal_incl_str="%.2f" % totaal_incl,
        verzend_str=verzend_str,
        gekozen_verzending=gekozen_verzending,
    )


@bp.route('/verwijderen/<int:product_id>', methods=['POST'])
def verwijderen(product_id):
    winkelwagen = session.get('winkelwagen', {})
    winkelwagen.pop(str(product_id), None)
    session['winkelwagen'] = winkelwagen
    return redirect(url_for('shop.winkelwagen'))


_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

def _valideer_checkout(form) -> list[str]:
    fouten = []
    verplichte_velden = [
        ('klant_naam',  'Naam'),
        ('klant_email', 'E-mailadres'),
        ('telefoon',    'Telefoonnummer'),
        ('straat',      'Straat en huisnummer'),
        ('postcode',    'Postcode'),
        ('stad',        'Stad'),
        ('land',        'Land'),
        ('verzending',  'Verzendmethode'),
    ]
    for key, label in verplichte_velden:
        if not form.get(key, '').strip():
            fouten.append(f'{label} is verplicht.')
    email = form.get('klant_email', '').strip()
    if email and not _EMAIL_RE.match(email):
        fouten.append('Vul een geldig e-mailadres in.')
    return fouten


@bp.route('/bestelling', methods=['POST'])
def bestelling():
    fouten = _valideer_checkout(request.form)
    if fouten:
        for f in fouten:
            flash(f, 'danger')
        return redirect(url_for('shop.winkelwagen'))

    klant_naam    = request.form['klant_naam'].strip()
    klant_email   = request.form['klant_email'].strip()
    telefoon      = request.form['telefoon'].strip()
    straat        = request.form['straat'].strip()
    postcode      = request.form['postcode'].strip()
    stad          = request.form['stad'].strip()
    land          = request.form['land'].strip()
    verzending    = request.form['verzending']
    betaalmethode = request.form.get('betaalmethode', 'ideal')

    verzend_kosten = 4.99 if verzending == 'express' else 0.0
    wagen = session.get('winkelwagen', {})
    totaal = sum(
        (db.session.get(Product, int(pid)) or Product()).prijs * n
        for pid, n in wagen.items()
        if db.session.get(Product, int(pid))
    )
    session['bestelling_data'] = {
        'klant_naam':    klant_naam,
        'klant_email':   klant_email,
        'telefoon':      telefoon,
        'straat':        straat,
        'postcode':      postcode,
        'stad':          stad,
        'land':          land,
        'verzending':    verzending,
        'betaalmethode': betaalmethode,
        'winkelwagen':   dict(wagen),
        'totaal_str':    "%.2f" % (totaal + verzend_kosten),
    }
    return redirect(url_for('shop.bestelling_betaal'))


@bp.route('/bestelling/betaal')
def bestelling_betaal():
    data = session.get('bestelling_data')
    if not data:
        flash('Geen bestelgegevens gevonden. Vul het formulier opnieuw in.', 'warning')
        return redirect(url_for('shop.winkelwagen'))
    wagen = session.get('winkelwagen', {})
    items = []
    for product_id, aantal in wagen.items():
        product = db.session.get(Product, int(product_id))
        if product:
            subtotaal = product.prijs * aantal
            items.append({'product': product, 'aantal': aantal, 'subtotaal': subtotaal})
    return render_template('betaal_bestelling.html',
        items=items,
        totaal_str=data['totaal_str'],
        klant_naam=data['klant_naam'],
        klant_email=data['klant_email'],
        telefoon=data['telefoon'],
        straat=data['straat'],
        postcode=data['postcode'],
        stad=data['stad'],
        land=data['land'],
        verzending=data['verzending'],
        betaalmethode=data['betaalmethode'],
    )


@bp.route('/bestelling/bevestig', methods=['POST'])
def bestelling_bevestig():
    klant_naam    = request.form.get('klant_naam')
    klant_email   = request.form.get('klant_email')
    telefoon      = request.form.get('telefoon')
    straat        = request.form.get('straat')
    postcode      = request.form.get('postcode')
    stad          = request.form.get('stad')
    land          = request.form.get('land')
    verzending    = request.form.get('verzending')
    betaalmethode = request.form.get('betaalmethode')
    wagen = session.get('winkelwagen', {})
    order = Order(
        klant_naam=klant_naam, klant_email=klant_email,
        telefoon=telefoon, straat=straat, postcode=postcode,
        stad=stad, land=land,
        verzendmethode=verzending, betaalmethode=betaalmethode,
    )
    db.session.add(order)
    db.session.flush()
    for product_id, aantal in wagen.items():
        product = db.session.get(Product, int(product_id))
        if product:
            db.session.add(OrderRegel(
                order_id=order.id, product_id=int(product_id),
                aantal=aantal, prijs_per_stuk=product.prijs,
            ))
            product.voorraad = max(0, product.voorraad - aantal)
    db.session.commit()
    session.pop('winkelwagen', None)
    session.pop('bestelling_data', None)
    flash(f'Order geplaatst, bedankt {klant_naam}! 🎉', 'success')
    return redirect(url_for('shop.shop'))


@bp.route('/doneer', methods=['GET', 'POST'])
def doneer():
    if request.method == 'POST':
        naam = request.form.get('naam', '').strip()
        email = request.form.get('email', '').strip()
        bericht = request.form.get('bericht', '').strip()
        eigen_bedrag = request.form.get('eigen_bedrag', '').strip()
        if not eigen_bedrag:
            flash('Vul een bedrag in.', 'warning')
            return redirect(url_for('shop.doneer'))
        try:
            bedrag = float(eigen_bedrag.replace(',', '.'))
        except ValueError:
            flash('Vul een geldig bedrag in.', 'warning')
            return redirect(url_for('shop.doneer'))
        session['donatie'] = {
            'naam': naam, 'email': email,
            'bedrag': bedrag, 'bericht': bericht,
            'betaalmethode': 'ideal',
        }
        return redirect(url_for('shop.donatie_betaal'))
    return render_template('doneer.html')


@bp.route('/doneer/betaal')
def donatie_betaal():
    donatie = session.get('donatie')
    if not donatie:
        flash('Geen donatie gevonden. Vul het formulier opnieuw in.', 'warning')
        return redirect(url_for('shop.doneer'))
    return render_template('betaal_donatie.html',
        naam=donatie['naam'], email=donatie['email'],
        bedrag=donatie['bedrag'], bericht=donatie.get('bericht'),
        betaalmethode=donatie['betaalmethode'],
    )


@bp.route('/doneer/bevestig', methods=['POST'])
def donatie_bevestig():
    from app.models import Donatie
    donatie_data = session.get('donatie')
    if not donatie_data:
        flash('Geen donatie gevonden.', 'warning')
        return redirect(url_for('shop.doneer'))
    donatie = Donatie(
        naam=donatie_data['naam'], email=donatie_data['email'],
        bedrag=donatie_data['bedrag'], bericht=donatie_data.get('bericht'),
    )
    db.session.add(donatie)
    db.session.commit()
    session.pop('donatie', None)
    flash(f'Dankjewel {donatie.naam}! 💜', 'success')
    return redirect(url_for('shop.doneer'))
