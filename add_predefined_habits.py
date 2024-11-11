# add_predefined_habits.py

import sqlite3
from datetime import datetime

DB_NAME = 'habits.db'

def setup_database():
    """
    Creates the 'habits' and 'completions' tables in the database if they do not exist.
    The 'habits' table stores information about each habit, while the 'completions'
    table tracks each completion record with date and time.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # Create 'habits' table with columns for habit name, frequency, creation date, and streak
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                name TEXT PRIMARY KEY,
                periodicity TEXT,
                created_at TEXT,
                streak INTEGER
            )
        """)
        
        # Create 'completions' table with date and time columns for each habit completion record
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS completions (
                habit_name TEXT,
                date TEXT,
                time TEXT,
                PRIMARY KEY (habit_name, date),
                FOREIGN KEY (habit_name) REFERENCES habits (name)
            )
        """)
        conn.commit()

def add_predefined_habits():
    """
    Adds five predefined habits to the 'habits' table in the database.
    If the habit already exists in the database, it will be skipped.
    """
    habits = [
        ("Exercise", "daily", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ("Read a book", "weekly", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ("Drink water", "daily", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ("Practice coding", "daily", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ("Clean the house", "weekly", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ]

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # Retrieve existing habit names to avoid duplicate entries
        cursor.execute("SELECT name FROM habits")
        existing_habits = set(row[0] for row in cursor.fetchall())

        # Insert each predefined habit if it does not already exist in the database
        for name, periodicity, created_at in habits:
            if name not in existing_habits:
                cursor.execute("INSERT INTO habits (name, periodicity, created_at, streak) VALUES (?, ?, ?, ?)",
                               (name, periodicity, created_at, 0))
        conn.commit()

# Ensure tables are set up, then add predefined habits for testing purposes
setup_database()
add_predefined_habits()
