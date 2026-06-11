import csv
import io
import os
from flask import Blueprint, render_template, redirect, request, url_for, flash, abort, current_app, make_response
from flask_babel import _
from werkzeug.utils import secure_filename
from app import db
from app.models import Product, Order
from app.auth import admin_required

_TOEGESTANE_EXTENSIES = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def _sla_foto_op(file):
    if not file or not file.filename:
        return None
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in _TOEGESTANE_EXTENSIES:
        return None
    filename = secure_filename(file.filename)
    upload_dir = os.path.join(current_app.root_path, 'static', 'img')
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, filename))
    return filename

bp = Blueprint('admin', __name__)


@bp.route('/admin')
@admin_required
def admin():
    from app.models import Donatie
    producten = Product.query.order_by(Product.id.desc()).all()
    orders = Order.query.order_by(Order.besteld_op.desc()).all()
    donaties = Donatie.query.order_by(Donatie.gedoneerd_op.desc()).all()
    edit_id = request.args.get('edit_id', type=int)
    tab = request.args.get('tab', 'producten')
    return render_template('admin.html',
        producten=producten, orders=orders,
        donaties=donaties, edit_id=edit_id, tab=tab,
    )


@bp.route('/admin/product/toevoegen', methods=['POST'])
@admin_required
def admin_add_product():
    naam = request.form.get('naam')
    beschrijving = request.form.get('beschrijving')
    prijs = float(request.form.get('prijs', 0))
    voorraad = int(request.form.get('voorraad', 0))
    foto = _sla_foto_op(request.files.get('foto_bestand')) or request.form.get('foto') or None
    db.session.add(Product(naam=naam, beschrijving=beschrijving, prijs=prijs, voorraad=voorraad, foto=foto))
    db.session.commit()
    flash(_('Product "%(naam)s" toegevoegd!', naam=naam), 'success')
    return redirect(url_for('admin.admin'))


@bp.route('/admin/product/<int:product_id>/wijzig', methods=['POST'])
@admin_required
def admin_wijzig_product(product_id):
    product = db.session.get(Product, product_id) or abort(404)
    product.naam = request.form.get('naam')
    product.beschrijving = request.form.get('beschrijving')
    product.prijs = float(request.form.get('prijs', product.prijs))
    product.voorraad = int(request.form.get('voorraad', product.voorraad))
    product.foto = (
        _sla_foto_op(request.files.get('foto_bestand'))
        or request.form.get('foto')
        or None
    )
    db.session.commit()
    flash(_('Product "%(naam)s" bijgewerkt!', naam=product.naam), 'success')
    return redirect(url_for('admin.admin'))


@bp.route('/admin/product/<int:product_id>/verwijder', methods=['POST'])
@admin_required
def admin_verwijder_product(product_id):
    product = db.session.get(Product, product_id) or abort(404)
    naam = product.naam
    db.session.delete(product)
    db.session.commit()
    flash(_('Product "%(naam)s" verwijderd.', naam=naam), 'success')
    return redirect(url_for('admin.admin'))


@bp.route('/admin/product/<int:product_id>/uitverkocht', methods=['POST'])
@admin_required
def admin_uitverkocht(product_id):
    product = db.session.get(Product, product_id) or abort(404)
    if product.voorraad == 0:
        product.voorraad = 10
        flash(_('"%(naam)s" terug op voorraad gezet (10 stuks).', naam=product.naam), 'success')
    else:
        product.voorraad = 0
        flash(_('"%(naam)s" gemarkeerd als uitverkocht.', naam=product.naam), 'warning')
    db.session.commit()
    return redirect(url_for('admin.admin'))


@bp.route('/admin/orders/export')
@admin_required
def admin_export_orders():
    orders = Order.query.order_by(Order.besteld_op.asc()).all()

    buf = io.StringIO()
    buf.write('﻿')  # UTF-8 BOM zodat Excel direct de juiste encoding herkent
    writer = csv.writer(buf)
    writer.writerow([
        'Order ID', 'Naam', 'Email', 'Telefoon',
        'Straat', 'Postcode', 'Stad', 'Land',
        'Verzendmethode', 'Betaalmethode', 'Besteld op',
        'Producten', 'Totaal (excl. verzending)',
    ])
    for order in orders:
        producten_str = '; '.join(
            f'{r.product.naam if r.product else "(verwijderd)"} x{r.aantal}'
            for r in order.regels
        )
        writer.writerow([
            order.id,
            order.klant_naam,
            order.klant_email,
            order.telefoon or '',
            order.straat or '',
            order.postcode or '',
            order.stad or '',
            order.land or '',
            order.verzendmethode or '',
            order.betaalmethode or '',
            order.besteld_op.strftime('%d-%m-%Y %H:%M'),
            producten_str,
            f'€{"%.2f" % order.totaal()}',
        ])

    response = make_response(buf.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=bestellingen.csv'
    return response


@bp.route('/admin/order/<int:order_id>/verwijder', methods=['POST'])
@admin_required
def admin_verwijder_order(order_id):
    order = db.session.get(Order, order_id) or abort(404)
    db.session.delete(order)
    db.session.commit()
    flash(_('Order verwijderd.'), 'success')
    return redirect(url_for('admin.admin'))
