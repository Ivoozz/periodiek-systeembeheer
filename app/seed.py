from app.database import engine, SessionLocal, Base
from app.models import User, Template, Category, Checkpoint
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Admin gebruiker
    admin = db.query(User).filter(User.username == "beheerder").first()
    if not admin:
        admin = User(username="beheerder", password_hash=pwd_context.hash("Welkom01!"), role="Behandelaar")
        db.add(admin)
        db.commit()
    else:
        print("User 'beheerder' already exists.")

    # Standaard Template
    tmpl = db.query(Template).filter(Template.name == "Standaard Systeembeheer").first()
    if not tmpl:
        tmpl = Template(name="Standaard Systeembeheer")
        db.add(tmpl)
        db.commit()
        db.refresh(tmpl)
    else:
        print("Template 'Standaard Systeembeheer' already exists.")

    # Data mapping
    data = {
        "Backup": ["Online Backup", "Lokale Backup", "Replicatie", "Gebackupte gegevens", "Alerting"],
        "Servermanagement": ["Eventlog", "Antivirus", "Password policy", "Schijfcontroller(s)", "Vrije schijfruimte", "Patchmanagement"],
        "Usermanagement": ["Actieve / non-actieve accounts", "Klant specifieke rechtengroepen", "Systeem rechtengroepen"],
        "Infrastructuur": ["Firewalllogs", "Firewall firmware versie", "Firewall regels", "Portscan", "Switchlogs", "Switch firmware versie", "Switch configuratie", "Switches online/offline", "UPS batterij", "UPS zelf test", "UPS configuratie", "UPS logs", "Alerting", "Netwerkverkeer", "Bandbreedte gebruik"],
        "Monitoring": ["Patchmanagement status", "Softwaremanagement", "Historie van Resourcegebruik"],
        "Security": ["2FA (elke inlog controleren)", "VPN-configuratie", "Antivirus logs", "Firewall beveiligingslogs", "Rechtengroepen met admin rechten", "Admingebruikers", "Voorwaardelijke toegang"]
    }

    for cat_name, items in data.items():
        cat = Category(name=cat_name, template_id=tmpl.id)
        db.add(cat)
        db.commit()
        for item in items:
            cp = Checkpoint(name=item, category_id=cat.id)
            db.add(cp)
    
    db.commit()
    db.close()
    print("Database seeding voltooid. Default login: beheerder / Welkom01!")

if __name__ == "__main__":
    seed_db()
