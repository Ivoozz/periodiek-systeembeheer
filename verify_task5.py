import sys
import os
sys.path.append(os.getcwd())

from app.db.database import SessionLocal
from app.db.models import User, Customer, Assignment, AssignmentStatus

def verify():
    db = SessionLocal()
    
    print("--- Verifying Users ---")
    users = db.query(User).all()
    for u in users:
        print(f"User: {u.username}, Role: {u.role}")
        
    print("\n--- Verifying Customers ---")
    customers = db.query(Customer).all()
    for c in customers:
        print(f"Customer: {c.name}, Contact: {c.contact_name}, Phone: {c.contact_phone}")
        
    print("\n--- Verifying Assignments ---")
    assignments = db.query(Assignment).all()
    for a in assignments:
        print(f"Assignment for {a.customer.name}, Tech: {a.technician.username}, Date: {a.scheduled_date}, Status: {a.status}, Recurring: {a.is_recurring}")
        
    db.close()

if __name__ == "__main__":
    verify()
