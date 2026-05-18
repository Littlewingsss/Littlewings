<div align="center">

<img src="app/static/img/logo.jpg" alt="Little Wings Logo" width="120" style="border-radius: 50%;" />

# 🕊️ Little Wings

### *Play · Heal · Fly*

**Little Wings** is een webshop met een missie: voor elk product dat je koopt, gaat 100% van de winst rechtstreeks naar kinderen die getroffen zijn door oorlog over de hele wereld. Eén aankoop, echte impact.

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.2.5-black?logo=flask)](https://flask.palletsprojects.com)
[![SQLite](https://img.shields.io/badge/Database-SQLite-lightblue?logo=sqlite)](https://sqlite.org)
[![Instagram](https://img.shields.io/badge/Instagram-@littlewings.heal-E1306C?logo=instagram&logoColor=white)](https://www.instagram.com/littlewings.heal)

</div>

---

## 🌸 Over het project

Little Wings is een initiatief dat kinderen in moeilijke situaties ondersteunt. Wij geloven dat creativiteit, kunst en muziek helpen bij het helen van trauma's. Door spel, muziek en creatieve activiteiten creëren we veilige ruimtes waar kinderen zich vrij voelen.

> *"Eén uur is genoeg om de dag van een kind te veranderen."*

---

## ✨ Features

- 🛍️ **Webshop** — Browse en bestel producten uit de Little Wings collectie
- 🛒 **Winkelwagen** — Voeg producten toe en beheer je bestelling
- 💳 **Checkout** — Bestel met keuze uit bezorgmethode en betaalmethode
- ❤️ **Donaties** — Doneer direct via een eenvoudig formulier
- 👤 **Gebruikersaccounts** — Registreer en log in om bestellingen te plaatsen
- 🔐 **Admin dashboard** — Beheer bestellingen, producten en donaties
- 📱 **Responsief design** — Werkt op desktop en mobiel

---

## 🗂️ Projectstructuur

```
Littlewings/
├── run.py                   # Startpunt van de applicatie
├── requirements.txt         # Python dependencies
├── app/
│   ├── __init__.py          # App factory (Flask setup)
│   ├── routes.py            # Alle URL-routes en logica
│   ├── models.py            # Database modellen
│   ├── forms.py             # WTForms formulieren
│   ├── auth.py              # Authenticatie helpers
│   ├── db.sqlite            # SQLite database
│   ├── static/
│   │   ├── css/style.css    # Styling
│   │   └── img/             # Productafbeeldingen & logo
│   └── templates/
│       ├── base.html        # Basis template
│       ├── home.html        # Homepagina
│       ├── shop.html        # Webshop
│       ├── winkelwagen.html # Winkelwagen
│       ├── betaal_bestelling.html  # Checkout bestelling
│       ├── betaal_donatie.html     # Checkout donatie
│       ├── doneer.html      # Donatiepagina
│       ├── over_ons.html    # Over ons pagina
│       ├── login.html       # Inloggen
│       ├── register.html    # Registreren
│       ├── welcome.html     # Welkomstpagina
│       └── admin.html       # Beheerpaneel
```

---

## 🚀 Installatie & opstarten

### Vereisten

- Python 3.10 of hoger
- pip

### Stappen

**1. Clone de repository**
```bash
git clone https://github.com/Littlewingsss/Littlewings.git
cd Littlewings
```

**2. Maak een virtuele omgeving aan**
```bash
python -m venv .venv
```

**3. Activeer de virtuele omgeving**

Op Windows:
```bash
.venv\Scripts\activate
```

Op macOS/Linux:
```bash
source .venv/bin/activate
```

**4. Installeer de dependencies**
```bash
pip install -r requirements.txt
```

**5. Start de applicatie**
```bash
python run.py
```

De app is nu beschikbaar op [http://localhost:5000](http://localhost:5000) 🎉

---

## 🗄️ Database modellen

| Model | Beschrijving |
|---|---|
| `User` | Gebruikersaccounts met gehashte wachtwoorden |
| `Product` | Producten met naam, beschrijving, prijs, voorraad en foto |
| `Order` | Bestellingen met klantgegevens, adres en betaalmethode |
| `OrderRegel` | Individuele producten per bestelling |
| `Donatie` | Directe donaties met naam, e-mail en bedrag |

---

## 🛠️ Technologieën

| Technologie | Gebruik |
|---|---|
| [Flask](https://flask.palletsprojects.com/) | Web framework |
| [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) | Database ORM |
| [Flask-Login](https://flask-login.readthedocs.io/) | Gebruikersauthenticatie |
| [Flask-WTF](https://flask-wtf.readthedocs.io/) | Formuliervalidatie |
| [Flask-Migrate](https://flask-migrate.readthedocs.io/) | Database migraties |
| [SQLite](https://sqlite.org/) | Database |
| [Jinja2](https://jinja.palletsprojects.com/) | HTML templates |

---

## 🌍 Onze impact

- 💚 **100% van de winst** gaat naar kinderen in oorlogsgebieden
- 🌱 **Duurzame materialen** in alle producten
- 🚚 **Gratis verzending** op alle bestellingen
- 🌐 **Wereldwijde impact** — elk klein gebaar telt

---

## 📱 Volg ons

Blijf op de hoogte van onze missie en zie hoe jouw steun het verschil maakt:

[![Instagram](https://img.shields.io/badge/Instagram-@littlewings.heal-E1306C?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/littlewings.heal)

---

## 🤝 Bijdragen

Wil je meehelpen? Pull requests zijn welkom! Voor grote wijzigingen, open eerst een issue om te bespreken wat je wilt veranderen.

---

<div align="center">

Gemaakt met ❤️ voor de kinderen van de wereld

**Little Wings** — *Play · Heal · Fly*

</div>
