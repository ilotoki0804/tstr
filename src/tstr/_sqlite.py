from __future__ import annotations

import sqlite3

from tstr import Template, normalize

__all__ = ["execute"]


def execute(cursor: sqlite3.Cursor, sql: Template) -> sqlite3.Cursor:
    """
    Executes SQL safely using template strings to prevent SQL injection.

    ```python
    # XXX: Using f-string (vulnerable to SQL injection):
    cursor.execute(f"SELECT * FROM users WHERE name = '{user_input}'")

    # Using template string (safe):
    execute(cursor, t"SELECT * FROM users WHERE name = {user_input}")
    ```

    Args:
        cursor (sqlite3.Cursor): The SQLite cursor to execute the SQL statement.
        sql (Template): The SQL statement as a template string.

    Returns:
        sqlite3.Cursor: The cursor after executing the SQL statement.
    """
    if not isinstance(sql, Template):
        raise TypeError(f"Expected Template, got {type(template).__name__}")

    query = []
    params = []
    for item in sql:
        if isinstance(item, str):
            query.append(item)
        else:
            query.append("?")
            params.append(normalize(item))
    return cursor.execute("".join(query), params)
