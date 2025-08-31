from __future__ import annotations

import typing
import sqlite3

from tstr import Template, normalize

if typing.TYPE_CHECKING:
    from sqlite3 import _Parameters

__all__ = ["build_query", "build_query_str", "execute", "TemplateCursor"]


def build_query(sql: Template) -> tuple[str, list]:
    if not isinstance(sql, Template):
        raise TypeError(f"can only build a query from tstr.Template (not {type(sql).__name__!r})")

    query = []
    params = []
    for item in sql:
        if isinstance(item, str):
            query.append(item)
        else:
            query.append("?")
            params.append(normalize(item))

    return "".join(query), params


def build_query_str(sql: typing.LiteralString | Template) -> tuple[str, list]:
    if isinstance(sql, str):
        return sql, []
    return build_query(sql)


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
    return cursor.execute(*build_query(sql))


class TemplateCursor(sqlite3.Cursor):
    def execute(self, sql: typing.LiteralString | Template, parameters: _Parameters = ()) -> typing.Self:  # type: ignore
        return super().execute(*build_query_str(sql))
