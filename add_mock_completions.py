# add_mock_completions.py

import sqlite3
from datetime import datetime, timedelta
from habit_tracker import Habit  # Import the Habit class to access update_streak

DB_NAME = 'habits.db'

def add_mock_completions():
    """
    Adds mock completion records to simulate user behavior over a span of four weeks.
    Each daily habit is marked as completed every day for four weeks, and each weekly
    habit is marked as completed once per week for four weeks.
    
    This helps populate the database with realistic data for testing analytics and streak calculations.
    """
    # Define habits and their periodicity
    daily_habits = ["Exercise", "Drink water", "Practice coding"]
    weekly_habits = ["Read a book", "Clean the house"]
    
    # Set today's date for calculating completion dates
    today = datetime.now().date()
    
    # Insert mock completion data into the database
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # Add completions for daily habits
        for habit_name in daily_habits:
            for days_ago in range(28):  # Completes for each day in 4 weeks
                completion_date = (today - timedelta(days=days_ago)).isoformat()  # Convert date to ISO format
                completion_time = datetime.now().strftime("%H:%M:%S")  # Current time for completion
                cursor.execute("INSERT INTO completions (habit_name, date, time) VALUES (?, ?, ?)",
                               (habit_name, completion_date, completion_time))
        
        # Add completions for weekly habits
        for habit_name in weekly_habits:
            for weeks_ago in range(4):  # Completes for each week in 4 weeks
                completion_date = (today - timedelta(weeks=weeks_ago)).isoformat()  # Convert date to ISO format
                completion_time = datetime.now().strftime("%H:%M:%S")  # Current time for completion
                cursor.execute("INSERT INTO completions (habit_name, date, time) VALUES (?, ?, ?)",
                               (habit_name, completion_date, completion_time))
        
        conn.commit()  # Save changes to the database

    # Update streaks for each habit based on the new completion records
    for habit_name in daily_habits + weekly_habits:
        habit = Habit(habit_name, "daily" if habit_name in daily_habits else "weekly")
        habit.update_streak()  # Calculate and save the streak for each habit
    print("Mock completion data has been successfully added to the database.")

# Run the function to add mock completions and update streaks for all habits
add_mock_completions()
