from __future__ import annotations

import sqlite3
from contextlib import closing

from tstr._sqlite import execute
from tstr import t


def test_execute():
    with closing(sqlite3.connect(":memory:")) as connection, closing(connection.cursor()) as cursor:
        execute(cursor, t("CREATE TABLE test(a, b)"))
        execute(cursor, t("INSERT INTO test VALUES ({1}, {2})"))
        execute(cursor, t("INSERT INTO test VALUES ({'1, 2); DROP TABLE test; --'}, {2})"))
        execute(cursor, t("INSERT INTO test VALUES ({'hello'!r}, {4})"))
        assert execute(cursor, t("SELECT * FROM test")).fetchall() == [(1, 2), ('1, 2); DROP TABLE test; --', 2), ("'hello'", 4)]
