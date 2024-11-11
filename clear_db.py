# clear_db.py

import sqlite3

DB_NAME = 'habits.db'

def clear_database():
    """
    Clears all data from the 'habits' and 'completions' tables in the database
    if these tables exist. This helps prevent errors if tables are missing.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # Check for 'habits' table existence before deletion
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='habits'")
        if cursor.fetchone():
            cursor.execute("DELETE FROM habits")
        
        # Check for 'completions' table existence before deletion
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='completions'")
        if cursor.fetchone():
            cursor.execute("DELETE FROM completions")
        
        conn.commit()
        print("Database cleared: All habits and completions have been deleted.")

if __name__ == '__main__':
    clear_database()
