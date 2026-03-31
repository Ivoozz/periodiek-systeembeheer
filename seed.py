import datetime
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.db.models import User, ChecklistTemplate, Category, Checkpoint, Customer, Assignment, AssignmentStatus, Role
from app.core.auth import get_password_hash

def seed_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Admin User
    admin = db.query(User).filter(User.username == "beheerder").first()
    if not admin:
        print(">>> Creating default admin: beheerder")
        admin = User(
            username="beheerder",
            password_hash=get_password_hash("Welkom01!"),
            role=Role.ADMIN,
            is_active=True
        )
        db.add(admin)
        db.commit()

    # 2. Technicus User
    tech = db.query(User).filter(User.username == "technicus1").first()
    if not tech:
        print(">>> Creating default technician: technicus1")
        tech = User(
            username="technicus1",
            password_hash=get_password_hash("Welkom01!"),
            role=Role.TECHNICUS,
            is_active=True
        )
        db.add(tech)
        db.commit()
    db.refresh(tech)

    # 3. Default Checklist Template
    template = db.query(ChecklistTemplate).first()
    if not template:
        print(">>> Creating default template: Standaard Systeembeheer")
        template = ChecklistTemplate(name="Standaard Systeembeheer", description="Maandelijkse controle")
        db.add(template)
        db.commit()
        db.refresh(template)

        # Categories
        cat1 = Category(template_id=template.id, name="Server Status", order=1)
        cat2 = Category(template_id=template.id, name="Backup & Security", order=2)
        db.add_all([cat1, cat2])
        db.commit()

        # Checkpoints
        cp1 = Checkpoint(category_id=cat1.id, name="Diskruimte", description="Controleer beschikbare ruimte")
        cp2 = Checkpoint(category_id=cat1.id, name="Systeem Updates", description="Check voor OS updates")
        cp3 = Checkpoint(category_id=cat2.id, name="Backups", description="Controleer laatste backup succes")
        cp4 = Checkpoint(category_id=cat2.id, name="Antivirus", description="Updates en scans controleren")
        db.add_all([cp1, cp2, cp3, cp4])
        db.commit()

    # 4. Customers
    cust1 = db.query(Customer).filter(Customer.name == "Bakkerij De Groot").first()
    if not cust1:
        print(">>> Creating customer: Bakkerij De Groot")
        cust1 = Customer(
            name="Bakkerij De Groot",
            location="Utrecht",
            contact_person="Jan de Groot",
            contact_name="Jan de Groot",
            contact_phone="030-1234567"
        )
        db.add(cust1)
        db.commit()
    db.refresh(cust1)

    cust2 = db.query(Customer).filter(Customer.name == "Slagerij Janssen").first()
    if not cust2:
        print(">>> Creating customer: Slagerij Janssen")
        cust2 = Customer(
            name="Slagerij Janssen",
            location="Amsterdam",
            contact_person="Piet Janssen",
            contact_name="Piet Janssen",
            contact_phone="020-7654321"
        )
        db.add(cust2)
        db.commit()
    db.refresh(cust2)

    # 5. Assignments
    assignment = db.query(Assignment).first()
    if not assignment:
        print(">>> Creating initial assignments")
        now = datetime.datetime.now()
        a1 = Assignment(
            customer_id=cust1.id,
            technician_id=tech.id,
            scheduled_date=now + datetime.timedelta(days=2),
            status=AssignmentStatus.PLANNED,
            is_recurring=True,
            interval_days=30
        )
        a2 = Assignment(
            customer_id=cust2.id,
            technician_id=tech.id,
            scheduled_date=now + datetime.timedelta(days=5),
            status=AssignmentStatus.PLANNED,
            is_recurring=False
        )
        db.add_all([a1, a2])
        db.commit()

    db.close()


if __name__ == "__main__":
    seed_db()
