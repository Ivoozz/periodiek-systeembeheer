import os
import sys
from app.db.database import get_connection

def migrate():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if customers.user_id exists
    cursor.execute("PRAGMA table_info(customers)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "user_id" not in columns:
        print(">>> Adding user_id to customers table")
        cursor.execute("ALTER TABLE customers ADD COLUMN user_id INTEGER REFERENCES users(id)")
    else:
        print(">>> user_id already exists in customers table")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Add root to sys.path to import app
    sys.path.append(os.getcwd())
    migrate()
