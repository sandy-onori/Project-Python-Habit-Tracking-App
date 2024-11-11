# File: habit_tracker.py

import sqlite3
from datetime import datetime, timedelta

DB_NAME = 'habits.db'

class Habit:
    """
    Represents a habit with attributes for name, periodicity, creation date, and streak.

    Attributes:
        name (str): The name of the habit.
        periodicity (str): The frequency of the habit ('daily' or 'weekly').
        created_at (datetime): The creation date of the habit.
        streak (int): The current streak count of the habit.
    """

    def __init__(self, name, periodicity, created_at=None):
        self.name = name
        self.periodicity = periodicity
        self.created_at = created_at or datetime.now()
        self.streak = 0

    def save(self):
        """Saves the habit to the database if it does not already exist."""
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO habits (name, periodicity, created_at, streak) VALUES (?, ?, ?, ?)",
                (self.name, self.periodicity, self.created_at.strftime("%Y-%m-%d %H:%M:%S"), self.streak)
            )
            conn.commit()

    def exists_in_db(self):
        """Checks if the habit exists in the database."""
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM habits WHERE name = ?", (self.name,))
            return cursor.fetchone() is not None

    def delete(self):
        """Deletes the habit and all associated completion records from the database."""
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM habits WHERE name = ?", (self.name,))
            cursor.execute("DELETE FROM completions WHERE habit_name = ?", (self.name,))
            conn.commit()

    def is_completed_today(self):
        """Checks if the habit has been completed today."""
        today_date = datetime.now().date().isoformat()
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM completions WHERE habit_name = ? AND date = ?", (self.name, today_date))
            return cursor.fetchone() is not None

    def is_completed_within_7_days(self):
        """Checks if the habit has been completed within the last 7 days."""
        today = datetime.now().date()
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT date FROM completions WHERE habit_name = ? ORDER BY date DESC LIMIT 1",
                (self.name,)
            )
            last_completion = cursor.fetchone()
            if last_completion:
                last_completion_date = datetime.strptime(last_completion[0], "%Y-%m-%d").date()
                return (today - last_completion_date).days < 7
            return False

    def complete_task(self, date=None):
        """
        Marks the habit as completed for a specific date, defaulting to today.

        Args:
            date (datetime, optional): The date of completion. Defaults to today.
        """
        if self.periodicity == "weekly":
            if self.is_completed_within_7_days():
                print(f"Habit '{self.name}' has already been completed within the last 7 days.")
                return
        elif self.periodicity == "daily" and self.is_completed_today() and date is None:
            print(f"Habit '{self.name}' has already been completed today.")
            return

        completion_date = (date or datetime.now()).date().isoformat()
        completion_time = datetime.now().strftime("%H:%M:%S")
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO completions (habit_name, date, time) VALUES (?, ?, ?)", 
                           (self.name, completion_date, completion_time))
            conn.commit()
            self.update_streak()

    def update_streak(self):
        """
        Updates the streak for the habit based on consecutive completion dates.
        Resets the streak if the periodicity pattern is broken.
        """
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT date FROM completions WHERE habit_name = ? ORDER BY date ASC", (self.name,))
            dates = [datetime.strptime(row[0], "%Y-%m-%d").date() for row in cursor.fetchall()]
            
            self.streak = 0
            if not dates:
                return

            # Start the streak with the first completion date
            self.streak = 1
            expected_date = dates[0]
            
            for date in dates[1:]:
                if self.periodicity == "daily":
                    if date == expected_date + timedelta(days=1):
                        self.streak += 1
                        expected_date = date
                    else:
                        break
                elif self.periodicity == "weekly":
                    # Check only day-level granularity (7 days apart)
                    if (date - expected_date).days >= 7:
                        self.streak += 1
                        expected_date = date
                    else:
                        break

            cursor.execute("UPDATE habits SET streak = ? WHERE name = ?", (self.streak, self.name))
            conn.commit()

    @staticmethod
    def update_all_streaks():
        """
        Updates streaks for all habits to ensure they are current.
        Loops through each habit, instantiates it, and calls update_streak.
        This ensures that any stale streak data is updated.
        """
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, periodicity FROM habits")
            habits = cursor.fetchall()

            for name, periodicity in habits:
                habit = Habit(name, periodicity)
                habit.update_streak()

def setup_database():
    """
    Initializes the database tables for habits and completions if they don't already exist.
    Ensures that 'habits' and 'completions' tables are created with necessary fields.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                name TEXT PRIMARY KEY,
                periodicity TEXT,
                created_at TEXT,
                streak INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS completions (
                habit_name TEXT,
                date TEXT,
                time TEXT,
                FOREIGN KEY (habit_name) REFERENCES habits (name),
                PRIMARY KEY (habit_name, date)
            )
        """)
        conn.commit()
