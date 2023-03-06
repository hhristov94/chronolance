import typer
import sqlite3
from datetime import datetime
from rich.table import Table
from rich.prompt import Prompt
from rich.console import Console
from chronolance.database import (
    add_work_session,
    update_session_end_time,
    update_session_description,
    delete_work_session,
    session_exists,
    fetch_current_sessions,
    has_ended,
)

console = Console()
app = typer.Typer()

conn = sqlite3.connect("work.db", detect_types=sqlite3.PARSE_DECLTYPES)
cur = conn.cursor()


def complete_name(incomplete: str):
    for session in fetch_current_sessions(cur):
        if session.name.startswith(incomplete):
            yield session.name


@app.command(short_help="Start a new work session")
def start(limit: str = typer.Option("", help="A limit for the work session")):
    idx, name = add_work_session(cur, conn, datetime.now(), limit)
    typer.echo(f"Work session {name}({idx}) started.")


@app.command(short_help="End a current work session")
def end(session_name: str = typer.Argument("", autocompletion=complete_name)):
    if session_exists(cur, session_name):
        if not has_ended(cur, session_name):
            update_session_end_time(cur, conn, session_name, datetime.now())
            typer.echo(f"Work session ended.")
            desc = Prompt.ask(
                "Write a short description of what you have done :sunglasses:"
            )
            update_session_description(cur, conn, session_name, desc)
        else:
            typer.echo(f"Session {session_name} has already ended.")
    else:
        typer.echo(f"Session {session_name} doesn't exists in the database.")


@app.command(short_help="Delete a work session")
def delete(session_name: str):
    if session_exists(cur, session_name):
        delete_work_session(cur, conn, session_name)
        typer.echo(f"Session {session_name} deleted.")
    else:
        typer.echo(f"Session {session_name} doesn't exists in the database.")


# TODO: add exports
# TODO: add reports
@app.command(short_help="Show today's work sessions and all currently open sessions")
def show():
    table = Table(show_header=True, header_style="cyan")
    table.add_column("Name", min_width=8, style="green")
    table.add_column("Status", min_width=6, justify="center", style="green")
    table.add_column("Elapsed", min_width=8)
    table.add_column("Left", min_width=8)
    table.add_column("Description", min_width=10)
    for session in fetch_current_sessions(cur):
        table.add_row(
            session.name,
            session.status(),
            session.elapsed(),
            session.remaining(),
            session.description,
        )
    console.print(table)


if __name__ == "__main__":
    app()
