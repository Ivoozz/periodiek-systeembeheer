import os
import sys
from app.db.database import get_connection

def migrate():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if users.display_name exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "display_name" not in columns:
        print(">>> Adding display_name to users table")
        cursor.execute("ALTER TABLE users ADD COLUMN display_name TEXT")
    else:
        print(">>> display_name already exists in users table")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Add root to sys.path to import app
    sys.path.append(os.getcwd())
    migrate()
