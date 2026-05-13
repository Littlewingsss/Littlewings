from app import db
from flask import current_app  
from flask import render_template, redirect, request, url_for, flash, Response, jsonify, session
from flask_login import login_user, login_required, logout_user
from app.models import User, Product, Order, OrderRegel
from app.forms import LoginForm, RegistrationForm
from app.auth import admin_required


def init_app(app):

    @app.route('/')
    def index():
        return render_template('welcome.html')

    @app.route('/home')
    @login_required
    def home():
        return render_template('home.html')

    @app.route('/logout')
    @login_required
    def logout() -> Response:
        logout_user()
        flash('Je bent nu uitgelogd!', 'success')
        return redirect(url_for('index'))

    @app.route('/login', methods=['GET', 'POST'])
    def login() -> str | Response:
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
            if user is not None and user.check_password(password):
                login_user(user)
                flash('Succesvol ingelogd.', 'success')
                return redirect(url_for('home'))

            flash('Verkeerd email of wachtwoord!', 'danger')
            return redirect(url_for('index'))

        return render_template('login.html', form=LoginForm())

    @app.route('/register', methods=['GET', 'POST'])
    def register() -> str | Response:
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm = request.form.get('confirm_password')

            if password != confirm:
                flash('Wachtwoorden komen niet overeen!', 'danger')
                return redirect(url_for('index'))

            bestaande_user = User.query.filter_by(username=username).first()
            bestaande_email = User.query.filter_by(email=email).first()

            if bestaande_user:
                flash('Gebruikersnaam is al in gebruik!', 'danger')
                return redirect(url_for('index'))

            if bestaande_email:
                flash('Email is al in gebruik!', 'danger')
                return redirect(url_for('index'))

            user = User(email=email, username=username, password=password)
            db.session.add(user)
            db.session.commit()
            flash('Dank voor de registratie. Je kan nu inloggen!', 'success')
            return redirect(url_for('index'))

        return render_template('register.html', form=RegistrationForm())

    @app.route('/over-ons')
    def over_ons():
        return render_template('over_ons.html')

    @app.route('/shop')
    def shop():
        productendb = Product.query.all()
        return render_template('shop.html', producten=productendb)


    @app.route('/toevoegen/<int:product_id>', methods=['POST'])
    def toevoegen(product_id):
        product = Product.query.get_or_404(product_id)
        winkelwagen = session.get('winkelwagen', {})
        key = str(product_id)
        huidige_aantal = winkelwagen.get(key, 0)

        if huidige_aantal >= product.voorraad:
            flash(f'Niet genoeg voorraad! Er zijn nog maar {product.voorraad} stuks beschikbaar.', 'danger')
            return redirect(url_for('shop'))

        winkelwagen[key] = huidige_aantal + 1
        session['winkelwagen'] = winkelwagen
        flash('Product toegevoegd aan je winkelwagen! 🛒', 'success')
        return redirect(url_for('shop')) 


    @app.route('/verhogen/<int:product_id>', methods=['POST'])
    def verhogen(product_id):
        product = Product.query.get_or_404(product_id)
        winkelwagen = session.get('winkelwagen', {})
        key = str(product_id)
        huidige_aantal = winkelwagen.get(key, 0)

        if huidige_aantal >= product.voorraad:
            flash(f'Niet genoeg voorraad! Er zijn nog maar {product.voorraad} stuks beschikbaar.', 'danger')
        else:
            winkelwagen[key] = huidige_aantal + 1
            session['winkelwagen'] = winkelwagen

        return redirect(url_for('winkelwagen'))

    @app.route('/verminderen/<int:product_id>', methods=['POST'])
    def verminderen(product_id):
        winkelwagen = session.get('winkelwagen', {})
        key = str(product_id)
        if key in winkelwagen:
            winkelwagen[key] -= 1
            if winkelwagen[key] <= 0:
                winkelwagen.pop(key)
        session['winkelwagen'] = winkelwagen
        return redirect(url_for('winkelwagen'))

    @app.route('/winkelwagen', methods=['GET', 'POST'])
    def winkelwagen():
        if request.method == 'POST':
            session['verzending'] = request.form.get('verzending', '')

        wagen = session.get('winkelwagen', {})
        gekozen_verzending = session.get('verzending', '')

        items = []
        totaal = 0
        for product_id, aantal in wagen.items():
            product = Product.query.get(int(product_id))
            if product:
                subtotaal = product.prijs * aantal
                totaal += subtotaal
                items.append({'product': product, 'aantal': aantal, 'subtotaal': subtotaal})

        verzend_kosten = 4.99 if gekozen_verzending == 'express' else 0.0
        verzend_str = '€ 4,99' if gekozen_verzending == 'express' else ('Gratis' if gekozen_verzending else '—')
        totaal_incl = totaal + verzend_kosten

        totaal_str = "%.2f" % totaal
        totaal_incl_str = "%.2f" % totaal_incl

        return render_template('winkelwagen.html', items=items, totaal_str=totaal_str, totaal_incl_str=totaal_incl_str, verzend_str=verzend_str, gekozen_verzending=gekozen_verzending) 

    @app.route('/verwijderen/<int:product_id>', methods=['POST'])
    def verwijderen(product_id):
        winkelwagen = session.get('winkelwagen', {})
        winkelwagen.pop(str(product_id), None)
        session['winkelwagen'] = winkelwagen
        return redirect(url_for('winkelwagen'))

    # ── Bestelling ───────────────────────────────────────────────────────────

    @app.route('/bestelling', methods=['POST'])
    def bestelling():
        klant_naam    = request.form.get('klant_naam')
        klant_email   = request.form.get('klant_email')
        telefoon      = request.form.get('telefoon')
        straat        = request.form.get('straat')
        postcode      = request.form.get('postcode')
        stad          = request.form.get('stad')
        land          = request.form.get('land')
        verzending    = request.form.get('verzending')
        betaalmethode = request.form.get('betaalmethode', 'ideal')

        
        verzend_kosten = 4.99 if verzending == 'express' else 0.0

        
        wagen = session.get('winkelwagen', {})
        totaal = 0
        items_snapshot = []
        for product_id, aantal in wagen.items():
            product = Product.query.get(int(product_id))
            if product:
                subtotaal = product.prijs * aantal
                totaal += subtotaal
                items_snapshot.append({
                    'product_id': int(product_id),
                    'naam': product.naam,
                    'aantal': aantal,
                    'subtotaal': subtotaal
                })

        totaal_incl = totaal + verzend_kosten

        
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
            'totaal_str':    "%.2f" % totaal_incl,
        }
        return redirect(url_for('bestelling_betaal'))

    @app.route('/bestelling/betaal')
    def bestelling_betaal():
        data = session.get('bestelling_data')
        if not data:
            flash('Geen bestelgegevens gevonden. Vul het formulier opnieuw in.', 'warning')
            return redirect(url_for('winkelwagen'))

        wagen = session.get('winkelwagen', {})
        items = []
        for product_id, aantal in wagen.items():
            product = Product.query.get(int(product_id))
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

    @app.route('/bestelling/bevestig', methods=['POST'])
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
            klant_naam     = klant_naam,
            klant_email    = klant_email,
            telefoon       = telefoon,
            straat         = straat,
            postcode       = postcode,
            stad           = stad,
            land           = land,
            verzendmethode = verzending,
            betaalmethode  = betaalmethode,
        )
        db.session.add(order)
        db.session.flush()  
        for product_id, aantal in wagen.items():
            product = Product.query.get(int(product_id))
            if product:
                regel = OrderRegel(
                    order_id       = order.id,
                    product_id     = int(product_id),
                    aantal         = aantal,
                    prijs_per_stuk = product.prijs,
                )
                db.session.add(regel)
                product.voorraad = max(0, product.voorraad - aantal)  

        db.session.commit()
        session.pop('winkelwagen', None)
        session.pop('bestelling_data', None)
        flash(f'Order geplaatst, bedankt {klant_naam}! 🎉', 'success')
        return redirect(url_for('shop'))

    # ── Donatie ──────────────────────────────────────────────────────────────

    @app.route('/doneer', methods=['GET', 'POST'])
    def doneer():
        if request.method == 'POST':
            naam = request.form.get('naam')
            email = request.form.get('email')
            bericht = request.form.get('bericht')
            eigen_bedrag = request.form.get('eigen_bedrag')
            

            if eigen_bedrag and eigen_bedrag.strip():
                try:
                    bedrag = float(eigen_bedrag.replace(',', '.'))
                except ValueError:
                    flash('Vul een geldig bedrag in.', 'warning')
                    return redirect(url_for('doneer'))
            else:
                flash('Vul een bedrag in.', 'warning')
                return redirect(url_for('doneer'))

            
            session['donatie'] = {
                'naam':         naam,
                'email':        email,
                'bedrag':       bedrag,
                'bericht':      bericht,
                'betaalmethode': 'ideal',  
            }
            return redirect(url_for('donatie_betaal'))

        return render_template('doneer.html')

    @app.route('/doneer/betaal')
    def donatie_betaal():
        donatie = session.get('donatie')

        if not donatie:
            flash('Geen donatie gevonden. Vul het formulier opnieuw in.', 'warning')
            return redirect(url_for('doneer'))

        return render_template('betaal_donatie.html',
            naam=donatie['naam'],
            email=donatie['email'],
            bedrag=donatie['bedrag'],
            bericht=donatie.get('bericht'), 
            betaalmethode=donatie['betaalmethode'],
        )

    @app.route('/doneer/bevestig', methods=['POST'])
    def donatie_bevestig():
        from app.models import Donatie

        donatie_data = session.get('donatie')  

        if not donatie_data:
            flash('Geen donatie gevonden.', 'warning')
            return redirect(url_for('doneer'))

        donatie = Donatie(
            naam=donatie_data['naam'],
            email=donatie_data['email'],
            bedrag=donatie_data['bedrag'],
            bericht=donatie_data.get('bericht')  
        )

        db.session.add(donatie)
        db.session.commit()

        session.pop('donatie', None)

        flash(f'Dankjewel {donatie.naam}! 💜', 'success')
        return redirect(url_for('doneer'))

    # ── Admin ────────────────────────────────────────────────────────────────

    @app.route('/admin')
    @admin_required
    def admin():
        from app.models import Donatie
        producten = Product.query.order_by(Product.id.desc()).all()
        orders = Order.query.order_by(Order.besteld_op.desc()).all()
        donaties = Donatie.query.order_by(Donatie.gedoneerd_op.desc()).all()
        edit_id = request.args.get('edit_id', type=int)
        tab = request.args.get('tab', 'producten')
        return render_template('admin.html',
            producten=producten,
            orders=orders,
            donaties=donaties,
            edit_id=edit_id,
            tab=tab,
        )

    @app.route('/admin/product/toevoegen', methods=['POST'])
    @admin_required
    def admin_add_product():
        naam = request.form.get('naam')
        beschrijving = request.form.get('beschrijving')
        prijs = float(request.form.get('prijs', 0))
        voorraad = int(request.form.get('voorraad', 0))
        foto = request.form.get('foto') or None
        product = Product(naam=naam, beschrijving=beschrijving, prijs=prijs, voorraad=voorraad, foto=foto)
        db.session.add(product)
        db.session.commit()
        flash(f'Product "{naam}" toegevoegd!', 'success')
        return redirect(url_for('admin'))

    @app.route('/admin/product/<int:product_id>/wijzig', methods=['POST'])
    @admin_required
    def admin_wijzig_product(product_id):
        product = Product.query.get_or_404(product_id)
        product.naam = request.form.get('naam')
        product.beschrijving = request.form.get('beschrijving')
        product.prijs = float(request.form.get('prijs', product.prijs))
        product.voorraad = int(request.form.get('voorraad', product.voorraad))
        product.foto = request.form.get('foto') or None
        db.session.commit()
        flash(f'Product "{product.naam}" bijgewerkt!', 'success')
        return redirect(url_for('admin'))

    @app.route('/admin/product/<int:product_id>/verwijder', methods=['POST'])
    @admin_required
    def admin_verwijder_product(product_id):
        product = Product.query.get_or_404(product_id)
        naam = product.naam
        db.session.delete(product)
        db.session.commit()
        flash(f'Product "{naam}" verwijderd.', 'success')
        return redirect(url_for('admin'))

    @app.route('/admin/product/<int:product_id>/uitverkocht', methods=['POST'])
    @admin_required
    def admin_uitverkocht(product_id):
        product = Product.query.get_or_404(product_id)
        if product.voorraad == 0:
            product.voorraad = 10
            flash(f'"{product.naam}" terug op voorraad gezet (10 stuks).', 'success')
        else:
            product.voorraad = 0
            flash(f'"{product.naam}" gemarkeerd als uitverkocht.', 'warning')
        db.session.commit()
        return redirect(url_for('admin'))

    @app.route('/admin/order/<int:order_id>/verwijder', methods=['POST'])
    @admin_required
    def admin_verwijder_order(order_id):
        order = Order.query.get_or_404(order_id)
        db.session.delete(order)
        db.session.commit()
        flash('Order verwijderd.', 'success')
        return redirect(url_for('admin'))