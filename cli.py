import click
from habit_tracker import Habit, setup_database
from analytics import (
    get_all_habits,
    get_incomplete_habits_for_today,
    get_habits_by_periodicity,
    longest_streak_all_habits,
    longest_streak_for_habit
)

@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--help', is_flag=True, is_eager=True, expose_value=False, callback=lambda ctx, param, value: print_cli_help(ctx) if value else None)
def cli(ctx):
    """
    CLI entry point for habit tracking commands. Initializes database setup and updates all streaks
    to ensure data is current before processing commands.

    Args:
        ctx: The context object, used to detect if a subcommand is invoked.
    """
    setup_database()
    Habit.update_all_streaks()
    if ctx.invoked_subcommand is None:
        print_cli_help(ctx)

def print_cli_help(ctx):
    """
    Prints a detailed help message for CLI commands, options, and examples.

    Args:
        ctx: The context object for CLI command grouping.
    """
    click.echo("""
Description:
  Habit Tracker CLI for managing and tracking habits.

Usage:
  python cli.py [OPTIONS] COMMAND [ARGS]

Options:
  --help     Show detailed usage.

Examples:
  python .\\cli.py add --help
  python .\\cli.py add "Shooting practice" daily

Commands:
  add                   Add a habit with a specific name and frequency (e.g., daily or weekly).
                            Example: python cli.py add "Exercise" daily

  check-today           Check if a habit has been completed today.
                            Example: python cli.py check-today "Exercise"

  complete              Mark a habit as completed for today.
                            Example: python cli.py complete "Exercise"

  delete                Remove a habit and all related completion records.
                            Example: python cli.py delete "Exercise"

  list-all              Show all habits being tracked.
                            Example: python cli.py list-all

  list-incomplete       Show habits that have not been completed today.
                            Example: python cli.py list-incomplete

  list-by-periodicity   Display habits filtered by frequency.
                            Example: python cli.py list-by-periodicity daily

  longest-streak        Show the longest streak across all habits.
                            Example: python cli.py longest-streak

  streak-for-habit      Show the longest streak for a specific habit by name.
                            Example: python cli.py streak-for-habit "Exercise"
""")
    ctx.exit()

@cli.command()
@click.argument('name')
@click.argument('periodicity', type=click.Choice(['daily', 'weekly']))
@click.option('--help', is_flag=True, is_eager=True, expose_value=False, callback=lambda ctx, param, value: print_add_help(ctx) if value else None)
def add(name, periodicity):
    """
    Adds a new habit to the database.

    Args:
        name: The name of the habit to add.
        periodicity: The frequency of the habit ('daily' or 'weekly').
    """
    habit = Habit(name, periodicity)
    if habit.exists_in_db():
        click.echo(f"Habit '{name}' already exists.")
    else:
        habit.save()
        click.echo(f"Habit '{name}' added with a periodicity of '{periodicity}'.")

def print_add_help(ctx):
    """
    Provides help information for the 'add' command.

    Args:
        ctx: The context object for CLI commands.
    """
    click.echo("""
Usage:
  python cli.py add NAME PERIODICITY

Arguments:
  NAME          The name of the habit to add, e.g., "Exercise".
  PERIODICITY   The frequency of the habit, choose from {daily|weekly}.

Examples:
  python cli.py add "Exercise" daily
  python cli.py add "Grocery shopping" weekly
""")
    ctx.exit()

@cli.command()
@click.argument('name')
@click.option('--help', is_flag=True, is_eager=True, expose_value=False, callback=lambda ctx, param, value: print_check_today_help(ctx) if value else None)
def check_today(name):
    """
    Checks if the specified habit has been completed today.

    Args:
        name: The name of the habit to check.
    """
    habit = Habit(name, periodicity="daily")
    if habit.exists_in_db():
        if habit.is_completed_today():
            click.echo(f"Habit '{name}' has already been completed today.")
        else:
            click.echo(f"Habit '{name}' has NOT been completed today.")
    else:
        click.echo(f"Habit '{name}' does not exist.")

def print_check_today_help(ctx):
    """
    Provides help information for the 'check-today' command.

    Args:
        ctx: The context object for CLI commands.
    """
    click.echo("""
Usage:
  python cli.py check-today NAME

Arguments:
  NAME          The name of the habit to check, e.g., "Exercise".

Example:
  python cli.py check-today "Exercise"
""")
    ctx.exit()

@cli.command()
@click.argument('name')
@click.option('--help', is_flag=True, is_eager=True, expose_value=False, callback=lambda ctx, param, value: print_complete_help(ctx) if value else None)
def complete(name):
    """
    Marks the specified habit as completed for today.

    Args:
        name: The name of the habit to mark as completed.
    """
    habit = Habit(name, periodicity="daily")
    if habit.exists_in_db():
        if habit.is_completed_today():
            click.echo(f"Habit '{name}' has already been completed today.")
        else:
            habit.complete_task()
            click.echo(f"Habit '{name}' marked as completed for today.")
    else:
        click.echo(f"Habit '{name}' does not exist.")

def print_complete_help(ctx):
    """
    Provides help information for the 'complete' command.

    Args:
        ctx: The context object for CLI commands.
    """
    click.echo("""
Usage:
  python cli.py complete NAME

Arguments:
  NAME          The name of the habit to mark as completed, e.g., "Exercise".

Example:
  python cli.py complete "Exercise"
""")
    ctx.exit()

@cli.command()
@click.argument('name')
@click.option('--help', is_flag=True, is_eager=True, expose_value=False, callback=lambda ctx, param, value: print_delete_help(ctx) if value else None)
def delete(name):
    """
    Deletes a habit and all associated completion records.

    Args:
        name: The name of the habit to delete.
    """
    habit = Habit(name, periodicity="daily")
    if habit.exists_in_db():
        habit.delete()
        click.echo(f"Habit '{name}' and its completions have been deleted.")
    else:
        click.echo(f"Habit '{name}' does not exist.")

def print_delete_help(ctx):
    """
    Provides help information for the 'delete' command.

    Args:
        ctx: The context object for CLI commands.
    """
    click.echo("""
Usage:
  python cli.py delete NAME

Arguments:
  NAME          The name of the habit to delete, e.g., "Exercise".

Example:
  python cli.py delete "Exercise"
""")
    ctx.exit()

@cli.command()
def list_all():
    """
    Lists all habits currently being tracked.
    """
    habits = get_all_habits()
    if habits:
        for habit in habits:
            click.echo(f"Habit: {habit[0]}, Periodicity: {habit[1]}, Created At: {habit[2]}, Streak: {habit[3]}")
    else:
        click.echo("No habits found.")

@cli.command()
@click.option('--help', is_flag=True, is_eager=True, expose_value=False, callback=lambda ctx, param, value: print_list_incomplete_help(ctx) if value else None)
def list_incomplete():
    """
    Lists habits that have not been completed today.
    """
    habits = get_incomplete_habits_for_today()
    if habits:
        for habit in habits:
            click.echo(f"Habit: {habit[0]}, Periodicity: {habit[1]}, Created At: {habit[2]}, Streak: {habit[3]}")
    else:
        click.echo("All habits have been completed for today.")

def print_list_incomplete_help(ctx):
    """
    Provides help information for the 'list-incomplete' command.

    Args:
        ctx: The context object for CLI commands.
    """
    click.echo("""
Usage:
  python cli.py list-incomplete

Description:
  List all habits that have not been completed today.

Example:
  python cli.py list-incomplete
""")
    ctx.exit()

@cli.command()
@click.argument('periodicity', type=click.Choice(['daily', 'weekly']))
@click.option('--help', is_flag=True, is_eager=True, expose_value=False, callback=lambda ctx, param, value: print_list_by_periodicity_help(ctx) if value else None)
def list_by_periodicity(periodicity):
    """
    Lists habits filtered by their specified periodicity.

    Args:
        periodicity: The periodicity to filter by ('daily' or 'weekly').
    """
    habits = get_habits_by_periodicity(periodicity)
    for habit in habits:
        click.echo(f"Habit: {habit[0]}, Periodicity: {habit[1]}, Created At: {habit[2]}, Streak: {habit[3]}")

def print_list_by_periodicity_help(ctx):
    """
    Provides help information for the 'list-by-periodicity' command.

    Args:
        ctx: The context object for CLI commands.
    """
    click.echo("""
Usage:
  python cli.py list-by-periodicity PERIODICITY

Arguments:
  PERIODICITY   The frequency of habits to list, choose from {daily|weekly}.

Examples:
  python cli.py list-by-periodicity daily
  python cli.py list-by-periodicity weekly
""")
    ctx.exit()

@cli.command()
@click.option('--help', is_flag=True, is_eager=True, expose_value=False, callback=lambda ctx, param, value: print_longest_streak_help(ctx) if value else None)
def longest_streak():
    """
    Displays the longest streak across all habits.
    """
    longest_streak = longest_streak_all_habits()
    click.echo(f"The longest streak across all habits is: {longest_streak}")

def print_longest_streak_help(ctx):
    """
    Provides help information for the 'longest-streak' command.

    Args:
        ctx: The context object for CLI commands.
    """
    click.echo("""
Usage:
  python cli.py longest-streak

Description:
  Show the longest streak across all habits.

Example:
  python cli.py longest-streak
""")
    ctx.exit()

@cli.command()
@click.argument('name')
@click.option('--help', is_flag=True, is_eager=True, expose_value=False, callback=lambda ctx, param, value: print_streak_for_habit_help(ctx) if value else None)
def streak_for_habit(name):
    """
    Displays the longest streak for a specific habit by name.

    Args:
        name: The name of the habit to display the streak for.
    """
    streak = longest_streak_for_habit(name)
    if streak is not None:
        click.echo(f"The longest streak for '{name}' is: {streak}")
    else:
        click.echo(f"Habit '{name}' does not exist.")

def print_streak_for_habit_help(ctx):
    """
    Provides help information for the 'streak-for-habit' command.

    Args:
        ctx: The context object for CLI commands.
    """
    click.echo("""
Usage:
  python cli.py streak-for-habit NAME

Arguments:
  NAME          The name of the habit to check the streak for, e.g., "Exercise".

Example:
  python cli.py streak-for-habit "Exercise"
""")
    ctx.exit()

if __name__ == '__main__':
    cli()
