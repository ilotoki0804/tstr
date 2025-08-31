from __future__ import annotations

import sqlite3
from contextlib import closing

import pytest

from tstr.ext._sqlite import build_query, build_query_str, execute, TemplateCursor
from tstr import t


def test_build_query():
    assert build_query_str("SELECT HELLO FROM WORLD") == ("SELECT HELLO FROM WORLD", [])
    with pytest.raises(TypeError, match="can only build a query from tstr.Template"):
        build_query("SELECT HELLO FROM WORLD")  # type: ignore

    assert build_query(t("INSERT INTO test VALUES ({1}, {2})")) == ("INSERT INTO test VALUES (?, ?)", [1, 2])
    hello = "world"
    assert build_query_str(t("INSERT INTO test VALUES ({1}, {hello})")) == ("INSERT INTO test VALUES (?, ?)", [1, "world"])


def test_execute():
    with closing(sqlite3.connect(":memory:")) as connection, closing(connection.cursor()) as cursor:
        execute(cursor, t("CREATE TABLE test(a, b)"))
        execute(cursor, t("INSERT INTO test VALUES ({1}, {2})"))
        execute(cursor, t("INSERT INTO test VALUES ({'1, 2); DROP TABLE test; --'}, {2})"))
        execute(cursor, t("INSERT INTO test VALUES ({'hello'!r}, {4})"))
        assert execute(cursor, t("SELECT * FROM test")).fetchall() == [(1, 2), ('1, 2); DROP TABLE test; --', 2), ("'hello'", 4)]


def test_cursor():
    with closing(sqlite3.connect(":memory:")) as connection, closing(connection.cursor(TemplateCursor)) as cursor:
        cursor.execute(t("CREATE TABLE test(a, b)"))
        cursor.execute(t("INSERT INTO test VALUES ({1}, {2})"))
        cursor.execute(t("INSERT INTO test VALUES ({'1, 2); DROP TABLE test; --'}, {2})"))
        cursor.execute(t("INSERT INTO test VALUES ({'hello'!r}, {4})"))
        assert cursor.execute(t("SELECT * FROM test")).fetchall() == [(1, 2), ('1, 2); DROP TABLE test; --', 2), ("'hello'", 4)]
