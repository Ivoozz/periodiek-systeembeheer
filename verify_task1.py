from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import get_connection
from app.db.models import User, Customer, WhitelabelSettings

def verify():
    engine = create_engine("sqlite://", creator=get_connection)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Check users
    users = session.query(User).all()
    print(f"Users found: {[u.username for u in users]}")
    
    # Check WhitelabelSettings
    whitelabel = session.query(WhitelabelSettings).all()
    print(f"Whitelabel entries: {len(whitelabel)}")
    if whitelabel:
        print(f"Brand name: {whitelabel[0].brand_name}")
        
    # Check Customers
    customers = session.query(Customer).all()
    for c in customers:
        print(f"Customer: {c.name}, user_id: {c.user_id}")
        
    session.close()

if __name__ == "__main__":
    verify()
