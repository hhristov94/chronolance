from sqlite3 import Connection, Cursor
from datetime import datetime
from typing import List

from chronolance.random_name import get_random_name
from chronolance.session import WorkSession


def create_table(cursor: Cursor) -> None:
    """
    Creates the work_sessions table if it doesn't exist.
    """
    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS work_sessions(
                id INTEGER PRIMARY KEY,
                name TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                description TEXT,
                session_limit TEXT)
        """
    )


def add_work_session(
    cursor: Cursor, connection: Connection, start_time: datetime, limit: str
) -> int:
    """
    Adds a new task to the work_sessions table.
    If the tasks table doesn't exist a new one is created implicitly.
    """
    create_table(cursor)
    session_name = get_random_name()
    cursor.execute(
        """
                  INSERT INTO work_sessions(start_time,
                                            name,
                                            session_limit)
                  VALUES(?, ?, ?)
                  """,
        [start_time, session_name, limit if limit else None],
    )
    connection.commit()
    return cursor.lastrowid, session_name


def session_exists(cursor: Cursor, session_name: str):
    """
    Checks if a given work session exists in the database.
    """
    cursor.execute(
        """
                  SELECT EXISTS(SELECT 1 FROM work_sessions WHERE name=:idx);
                  """,
        {"idx": session_name},
    )
    return cursor.fetchone()[0]


def has_ended(cursor: Cursor, session_name: str):
    """
    Checks if a given work session has ended.
    """
    cursor.execute(
        """
                  SELECT EXISTS(SELECT 1 
                                FROM work_sessions 
                                WHERE name=:idx 
                                AND end_time IS NOT NULL);
                  """,
        {"idx": session_name},
    )
    return cursor.fetchone()[0]


def fetch_current_sessions(cursor: Cursor) -> List[WorkSession]:
    """
    Retrieves today's work sessions from the work_sessions table.
    """
    cursor.execute(
        """SELECT * FROM work_sessions
                      WHERE DATE(start_time) = DATE()
                      OR end_time IS NULL"""
    )
    return [WorkSession(*row) for row in cursor.fetchall()]


def delete_work_session(
    cursor: Cursor, connection: Connection, session_name: str
) -> None:
    """
    Deletes a work session  from the work_sessions table by session_id.
    """
    cursor.execute("DELETE FROM work_sessions WHERE name=:idx", {"idx": session_name})
    connection.commit()


def update_session_end_time(
    cursor: Cursor, connection: Connection, session_name: str, end_time: datetime
) -> None:
    """
    Updates a work session's end_time from the work_sessions table by session_id.
    """

    cursor.execute(
        """
                  UPDATE work_sessions
                  SET end_time = :end
                  WHERE name=:idx""",
        {"idx": session_name, "end": end_time},
    )
    connection.commit()


def update_session_description(
    cursor: Cursor, connection: Connection, session_name: str, session_description: str
) -> None:
    """
    Updates a work session's description from the work_sessions table by session_id.
    """

    cursor.execute(
        """
                  UPDATE work_sessions
                  SET description = :desc
                  WHERE name=:idx""",
        {"idx": session_name, "desc": session_description},
    )
    connection.commit()
