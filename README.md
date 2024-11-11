
# Habit Tracker CLI Application

## Table of Contents
1. [Description](#1-description)
2. [Installation](#2-installation)
   - [Prerequisites](#prerequisites)
   - [Steps](#steps)
3. [Database Setup](#3-database-setup)
4. [Features](#4-features)
5. [Usage Guide](#5-usage-guide)
6. [Manual Testing](#6-manual-testing)
7. [Testing](#7-testing)

## 1 Description

The Habit Tracker CLI Application is a command-line tool that helps users build and maintain habits by allowing them to create, manage, and track their daily and weekly goals. With features like streak tracking, analytics, and habit categorization, this application enables users to monitor their progress and stay consistent with their routines.

## 2 Installation

### Prerequisites

- [Python](https://www.python.org/downloads/release/python-3127/) 3.12.7 or higher 
- [pip](https://pip.pypa.io/en/stable/installation/) for Python package management

### Steps

1. **Install Dependencies**:
   Run the following command to install required packages:
   ```bash
   pip install click pytest
   ```

2. **Set Up Environment**:
   If you have specific environment configurations (e.g., virtual environments), activate them as needed. However, no specific environment setup is mandatory for this project.

## 3 Database Setup

The application uses SQLite for data storage. You can initialize or clear the database with the provided scripts.
Also remember that running the test_habit_tracker.py file will re-initialize, emptying, the database. So if you plan to run the test file, do it before populating with your data.

0. **(Optional) Run the tests**:
   ```bash
   python test_habit_tracker.py
   ```

1. **Add the 5 predefined habits**:
   ```bash
   python add_predefined_habits.py
   ```
2. **Add the mock completion data**:
   ```bash
   python add_mock_completions.py
   ```

If you have run these 3 steps (0, 1 and 2), you will have tested the application, emptied and re-initialized, and populated the database with mock data.
Now, if you should see 5 records if you type:
  ```bash
   python list-all.py
   ```
You are all set up and good to go!

## 4 Features

- **Add and Manage Habits**: Add habits with daily or weekly tracking options, and manage their details.
- **Completion Tracking**: Mark habits as completed, and automatically calculate streaks based on completion dates.
- **Analytics**:
  - View all habits and filter by periodicity.
  - See incomplete habits for the day.
  - Check the longest streak for a specific habit or across all habits.
- **Delete Habits**: Remove habits and all associated completion records.

## 5 Usage Guide

Run the following commands from the CLI to interact with the application:

- **Add a Habit**:
  ```bash
  python cli.py add "Exercise" daily
  ```
  
- **Mark a Habit as Completed**:
  ```bash
  python cli.py complete "Exercise"
  ```
  
- **View All Habits**:
  ```bash
  python cli.py list-all
  ```

- **View Incomplete Habits for Today**:
  ```bash
  python cli.py list-incomplete
  ```

- **Delete a Habit**:
  ```bash
  python cli.py delete "Exercise"
  ```

- **Check Longest Streak for a Habit**:
  ```bash
  python cli.py streak-for-habit "Exercise"
  ```

- **Check Longest Streak Across All Habits**:
  ```bash
  python cli.py longest-streak
  ```

## 6 Manual Testing

You can manually test the application for edge-case behavior by performing the following actions:

- **Trying to add a habit with the same name**:
  Attempt to add a habit that already exists in the database. The application should notify you that the habit is a duplicate.
  ```bash
  python cli.py add "Exercise" daily
  python cli.py add "Exercise" daily  # This should show a message that the habit already exists.
  ```

- **Trying to delete a habit that does not exist**:
  Attempt to delete a habit that is not present in the database. The application should notify you that the habit does not exist.
  ```bash
  python cli.py delete "NonExistentHabit"  # This should indicate that the habit doesn't exist.
  ```

- **Trying to complete an already completed task**:
  Complete a habit, then attempt to mark it as completed again on the same day. The application should notify you that the habit has already been completed for today.
  ```bash
  python cli.py complete "Exercise"
  python cli.py complete "Exercise"  # This should indicate that "Exercise" has already been completed today.
  ```

## 7 Testing

To test the core functionalities of the application, run the test suite using pytest:

```bash
pytest test_habit_tracker.py
```

Each test is isolated with a fresh database setup and teardown, ensuring accurate results for habit creation, tracking, and analytics.
