from app import create_app, db
from app.models import Product
 
app = create_app()
with app.app_context():
    
    Product.query.delete()
    db.session.commit()
 
    producten = [
        Product(
            naam="Hope Hoodie",
            beschrijving="Zachte paarse hoodie met Little Wings logo.",
            prijs=39.99,
            voorraad=10,
            foto="hope-hoodie.png"
        ),
        Product(
            naam="Little Wings Classic Tee",
            beschrijving="Lichtgewicht T-shirt met Little Wings graphic en boodschap.",
            prijs=21.99,
            voorraad=15,
            foto="Littele Wings Classic Tee.png"
        ),
        Product(
            naam="Cotton Cap",
            beschrijving="Lichtblauwe katoenen cap met Little Wings logo.",
            prijs=19.99,
            voorraad=10,
            foto="Little Wings Cap.png"
        ),
        Product(
            naam="Wings of Hope Keychain",
            beschrijving="Sleutelhanger met vleugels als symbool van hoop.",
            prijs=9.99,
            voorraad=20,
            foto="Wings of Hope Keychain.png"
        ),
        Product(
            naam="Gano7 Comfort Bear",
            beschrijving="Een knuffelige beer geïnspireerd door Gano7.",
            prijs=24.99,
            voorraad=8,
            foto="Gano7 Comfort Bear.png"
        ),
        Product(
            naam="Dream Big Puzzle",
            beschrijving="Hartverwarmende puzzel met een hoopvolle boodschap.",
            prijs=16.99,
            voorraad=10,
            foto="Dream Big Bear.png"
        ),
        Product(
            naam="Support Healing Hoodie",
            beschrijving="Donkerblauwe hoodie met Little Wings boodschap.",
            prijs=39.99,
            voorraad=10,
            foto="Support Healing Hoodie.png"
        ),
        Product(
            naam="Awareness Bracelet",
            beschrijving="Armband met een steunende boodschap.",
            prijs=10.99,
            voorraad=25,
            foto="Awareness Bracelet.png"
        ),
        Product(
            naam="Healing Wings Stickers",
            beschrijving="4 stickers voor steun en heling.",
            prijs=6.99,
            voorraad=30,
            foto="Healing Wings Stckers.png"
        ),
        Product(
            naam="Gano7 Hoodie",
            beschrijving="Little Wings Crew hoodie met Gano7 karakter.",
            prijs=34.99,
            voorraad=10,
            foto="Gano7 Hoodie.png"
        ),
        Product(
            naam="Dream Big Bear",
            beschrijving="Teddybeer met kleine vleugels.",
            prijs=21.99,
            voorraad=8,
            foto="Dream Big Bear.png"
        ),
        Product(
            naam="Gano7 Keychain",
            beschrijving="Sleutelhanger met Gano7 karakter.",
            prijs=8.99,
            voorraad=2,
            foto="Gano7 Keychain.png"
        ),
    ]
    with db.engine.connect() as conn:
        db.create_all()
        bestaande_kolommen = [
            row[1] for row in conn.execute(db.text("PRAGMA table_info(orders)"))
        ]
            
        if 'telefoon' not in bestaande_kolommen:
            conn.execute(db.text("ALTER TABLE orders ADD COLUMN telefoon VARCHAR(30)"))
        if 'straat' not in bestaande_kolommen:
            conn.execute(db.text("ALTER TABLE orders ADD COLUMN straat VARCHAR(200)"))
        if 'postcode' not in bestaande_kolommen:
            conn.execute(db.text("ALTER TABLE orders ADD COLUMN postcode VARCHAR(20)"))
        if 'stad' not in bestaande_kolommen:
            conn.execute(db.text("ALTER TABLE orders ADD COLUMN stad VARCHAR(100)"))
        if 'land' not in bestaande_kolommen:
            conn.execute(db.text("ALTER TABLE orders ADD COLUMN land VARCHAR(100)"))
        if 'verzendmethode' not in bestaande_kolommen:
            conn.execute(db.text("ALTER TABLE orders ADD COLUMN verzendmethode VARCHAR(100)"))
        if 'betaalmethode' not in bestaande_kolommen:
            conn.execute(db.text("ALTER TABLE orders ADD COLUMN betaalmethode VARCHAR(50)"))
        if 'verzonden' not in bestaande_kolommen:
            conn.execute(db.text("ALTER TABLE orders ADD COLUMN verzonden BOOLEAN DEFAULT 0"))
        
        conn.commit()
 
    db.session.add_all(producten)
    db.session.commit()
    print(f"{len(producten)} producten toegevoegd!")