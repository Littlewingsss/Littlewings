from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, Integer, ForeignKey, Text, DateTime
from datetime import datetime


@login_manager.user_loader
def load_user(user_id: int):
    return db.session.get(User, int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(128))

    def __init__(self, email: str, username: str, password: str):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    __tablename__ = 'product'
    id: Mapped[int] = mapped_column(primary_key=True)
    naam: Mapped[str] = mapped_column(String(100), nullable=False)
    beschrijving: Mapped[str | None] = mapped_column(Text)
    prijs: Mapped[float] = mapped_column(Float, nullable=False)
    voorraad: Mapped[int] = mapped_column(Integer, default=0)
    foto: Mapped[str | None] = mapped_column(String(200))
    def __repr__(self):
        return f'<Product {self.naam}>'

class Order(db.Model):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    klant_naam: Mapped[str] = mapped_column(String(100), nullable=False)
    klant_email: Mapped[str] = mapped_column(String(120), nullable=False)
    telefoon: Mapped[str | None] = mapped_column(String(30), nullable=True)
    straat: Mapped[str | None] = mapped_column(String(200), nullable=True)
    postcode: Mapped[str | None] = mapped_column(String(20), nullable=True)
    stad: Mapped[str | None] = mapped_column(String(100), nullable=True)
    land: Mapped[str | None] = mapped_column(String(100), nullable=True)
    besteld_op: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    verzendmethode: Mapped[str | None] = mapped_column(String(100), nullable=True)
    betaalmethode: Mapped[str | None] = mapped_column(String(50), nullable=True)
    regels: Mapped[list['OrderRegel']] = db.relationship('OrderRegel', back_populates='order', cascade='all, delete-orphan')

    def totaal(self):
        return sum(r.prijs_per_stuk * r.aantal for r in self.regels)

    def __repr__(self):
        return f'<Order #{self.id} {self.klant_naam}>'


class OrderRegel(db.Model):
    __tablename__ = 'order_regels'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('product.id'), nullable=False)
    aantal: Mapped[int] = mapped_column(Integer, default=1)
    prijs_per_stuk: Mapped[float] = mapped_column(Float, nullable=False)
    order: Mapped['Order'] = db.relationship('Order', back_populates='regels')
    product: Mapped['Product'] = db.relationship('Product')

    def __repr__(self):
        return f'<OrderRegel order={self.order_id} product={self.product_id}>'


class Donatie(db.Model):
    __tablename__ = 'donaties'
    id: Mapped[int] = mapped_column(primary_key=True)
    naam: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    bedrag: Mapped[float] = mapped_column(Float, nullable=False)
    bericht: Mapped[str | None] = mapped_column(Text)
    gedoneerd_op: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<Donatie {self.naam} €{self.bedrag}>'