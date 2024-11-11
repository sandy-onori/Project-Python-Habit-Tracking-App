# File: test_habit_tracker.py

import pytest
from datetime import datetime, timedelta
import sqlite3
from habit_tracker import Habit, setup_database
from analytics import (
    get_all_habits,
    get_incomplete_habits_for_today,
    get_habits_by_periodicity,
    longest_streak_all_habits,
    longest_streak_for_habit
)

DB_NAME = 'habits.db'

@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    """
    Fixture to set up a fresh database and clean up after each test.
    Creates the tables before each test and clears all data from them after each test.
    """
    setup_database()  # Initialize database tables
    yield
    # Teardown: Clear all data from the database after each test
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM habits")
        cursor.execute("DELETE FROM completions")
        conn.commit()

def test_create_habit():
    """Test if a habit can be created and stored in the database."""
    habit = Habit("Exercise", "daily")
    habit.save()
    assert habit.exists_in_db()

def test_add_completion_and_streak_calculation_daily():
    """Test daily habit completion tracking and streak calculation with date and time."""
    habit = Habit("Exercise", "daily")
    habit.save()
    now = datetime.now()

    # Complete tasks for today and the past 4 days
    for i in range(5):
        habit.complete_task(date=now - timedelta(days=i))
        habit.update_streak()

    assert habit.streak == 5

    # Verify completion date and time entries in the database
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT date, time FROM completions WHERE habit_name = ?", (habit.name,))
        results = cursor.fetchall()

    assert len(results) == 5
    for date, time in results:
        assert date is not None
        assert time is not None

def test_add_completion_and_streak_calculation_weekly():
    """Test weekly habit completion tracking and streak calculation with date and time."""
    habit = Habit("Read a book", "weekly")
    habit.save()
    now = datetime.now()

    # Temporarily bypass the 7-day completion check for testing purposes
    def complete_task_bypass(habit, date=None):
        completion_date = (date or datetime.now()).date().isoformat()
        completion_time = datetime.now().strftime("%H:%M:%S")
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO completions (habit_name, date, time) VALUES (?, ?, ?)", 
                           (habit.name, completion_date, completion_time))
            conn.commit()
        habit.update_streak()

    # Complete tasks exactly 7 days apart for 4 weeks
    for i in range(4):
        completion_date = now - timedelta(days=7 * i)
        complete_task_bypass(habit, date=completion_date)

    # Verify the streak count after bypassing 7-day restriction
    assert habit.streak == 4

    # Verify completion date and time entries in the database
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT date, time FROM completions WHERE habit_name = ?", (habit.name,))
        results = cursor.fetchall()

    assert len(results) == 4
    for date, time in results:
        assert date is not None
        assert time is not None

def test_check_today_completed():
    """Test if a habit is correctly identified as completed today with date and time."""
    habit = Habit("Meditation", "daily")
    habit.save()
    habit.complete_task(date=datetime.now())
    
    assert habit.is_completed_today() == True

def test_check_today_not_completed():
    """Test if a habit is correctly identified as not completed today."""
    habit = Habit("Reading", "daily")
    habit.save()

    assert habit.is_completed_today() == False

def test_longest_streak_all_habits():
    """Test analytics for the longest streak across all habits."""
    habit1 = Habit("Exercise", "daily")
    habit2 = Habit("Read a book", "weekly")
    habit1.save()
    habit2.save()

    now = datetime.now()
    for i in range(10):
        habit1.complete_task(date=now - timedelta(days=i))
        habit1.update_streak()

    for i in range(4):
        completion_date = now - timedelta(weeks=i)
        habit2.complete_task(date=completion_date)
        habit2.update_streak()

    longest_streak = longest_streak_all_habits()
    assert longest_streak == 10

def test_longest_streak_for_specific_habit():
    """Test longest streak for a specific habit."""
    habit = Habit("Exercise", "daily")
    habit.save()

    now = datetime.now()
    for i in range(7):
        habit.complete_task(date=now - timedelta(days=i))
        habit.update_streak()

    longest_streak_exercise = longest_streak_for_habit("Exercise")
    assert longest_streak_exercise == 7

def test_get_habits_by_periodicity():
    """Test that habits are correctly filtered by periodicity."""
    habit1 = Habit("Exercise", "daily")
    habit2 = Habit("Read a book", "weekly")
    habit3 = Habit("Drink water", "daily")
    habit1.save()
    habit2.save()
    habit3.save()

    daily_habits = get_habits_by_periodicity("daily")
    weekly_habits = get_habits_by_periodicity("weekly")

    assert len(daily_habits) == 2
    assert len(weekly_habits) == 1

def test_daily_streak_breaks_on_skip():
    """Test that the streak for a daily habit breaks if one day is missed."""
    habit = Habit("Exercise", "daily")
    habit.save()
    now = datetime.now()

    # Complete tasks for today, yesterday, and two days ago, skipping one day
    habit.complete_task(date=now)
    habit.complete_task(date=now - timedelta(days=1))
    habit.complete_task(date=now - timedelta(days=3))  # Skipping day 2
    habit.update_streak()

    # Expect streak to be 1 as the consecutive completion is broken by the skip
    assert habit.streak == 1

def test_weekly_streak_breaks_on_skip():
    """Test that the streak for a weekly habit breaks if one week is missed."""
    habit = Habit("Read a book", "weekly")
    habit.save()
    now = datetime.now()

    # Complete tasks for this week, skip one week, then complete the week after
    habit.complete_task(date=now)
    habit.complete_task(date=now - timedelta(weeks=2))  # Skipping one week
    habit.update_streak()

    # Expect streak to be 1 as the consecutive weekly completion is broken by the skip
    assert habit.streak == 1

def test_weekly_habit_completion_within_7_days():
    """Test if a weekly habit correctly identifies completion within the last 7 days."""
    habit = Habit("Weekly Review", "weekly")
    habit.save()
    
    # Mark as completed today
    habit.complete_task(date=datetime.now())
    assert habit.is_completed_within_7_days() == True  # Should be completed within last 7 days
    
    # Try completing again within 7 days, expect no completion
    habit.complete_task()  # This should not add a new completion due to within-7-days rule
    
    # Verify only one completion exists in the database
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM completions WHERE habit_name = ?", (habit.name,))
        completion_count = cursor.fetchone()[0]
    
    assert completion_count == 1  # Only one completion should exist
