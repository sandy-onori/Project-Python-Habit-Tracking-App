# analytics.py

import sqlite3
from datetime import datetime, timedelta

DB_NAME = 'habits.db'

def get_all_habits():
    """
    Retrieves all habits from the database.
    
    Returns:
        list of tuple: Each tuple contains habit details (name, periodicity, created_at, streak).
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, periodicity, created_at, streak FROM habits")
        return cursor.fetchall()

def get_incomplete_habits_for_today():
    """
    Retrieves all daily habits not completed today and weekly habits not completed within the last 7 days.
    
    Returns:
        list of tuple: List of tuples representing incomplete habits with their details.
    """
    today_date = datetime.now().date().isoformat()
    seven_days_ago = (datetime.now().date() - timedelta(days=7)).isoformat()

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        # Retrieve incomplete daily habits
        cursor.execute("""
            SELECT name, periodicity, created_at, streak
            FROM habits
            WHERE periodicity = 'daily' 
            AND name NOT IN (SELECT habit_name FROM completions WHERE date = ?)
        """, (today_date,))
        incomplete_daily = cursor.fetchall()

        # Retrieve incomplete weekly habits
        cursor.execute("""
            SELECT name, periodicity, created_at, streak
            FROM habits
            WHERE periodicity = 'weekly'
            AND name NOT IN (SELECT habit_name FROM completions WHERE date >= ?)
        """, (seven_days_ago,))
        incomplete_weekly = cursor.fetchall()

        # Combine and return both lists
        return incomplete_daily + incomplete_weekly

def get_habits_by_periodicity(periodicity):
    """
    Retrieves habits by their periodicity type.

    Args:
        periodicity (str): The frequency of the habits ('daily' or 'weekly').

    Returns:
        list of tuple: List of tuples representing habits matching the specified periodicity.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, periodicity, created_at, streak FROM habits WHERE periodicity = ?", (periodicity,))
        return cursor.fetchall()

def longest_streak_all_habits():
    """
    Finds the longest streak among all habits.

    Returns:
        int or None: The maximum streak found in the 'habits' table, or None if no entries.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(streak) FROM habits")
        result = cursor.fetchone()
        return result[0] if result else 0

def longest_streak_for_habit(name):
    """
    Finds the longest streak for a specific habit.

    Args:
        name (str): The name of the habit.

    Returns:
        int or None: The streak for the specified habit, or None if the habit is not found.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT streak FROM habits WHERE name = ?", (name,))
        result = cursor.fetchone()
        return result[0] if result else None
