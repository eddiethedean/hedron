import pytest

from hedron_core.diagnostics import HedronError
from hedron_data.snowflake_source import SnowflakeDataSource, assert_select_only


class _Cur:
    description = (("ID",), ("NAME",))

    def __init__(self) -> None:
        self._sql = ""

    def execute(self, sql, params=()):
        self._sql = sql

    def fetchmany(self, n):
        return [(1, "a")][:n]

    def fetchone(self):
        return (1,)

    def close(self):
        return None


class _Conn:
    def cursor(self):
        return _Cur()

    def close(self):
        return None


def test_snowflake_bounded_fetch() -> None:
    src = SnowflakeDataSource(connection_factory=_Conn, statement="SELECT id, name FROM t")
    page = src.fetch(__import__("hedron_data.sources", fromlist=["DataQuery"]).DataQuery(limit=10))
    assert page.total == 1
    assert page.rows


@pytest.mark.parametrize(
    "statement",
    [
        "INSERT INTO t SELECT 1",
        "DELETE FROM t -- select",
        "UPDATE t SET x=1 WHERE id IN (SELECT id FROM t)",
        "SELECT 1; DROP TABLE t",
        "WITH x AS (SELECT 1 AS n) INSERT INTO t SELECT * FROM x",
        "SELECT id, email FROM customers INTO TABLE attacker_copy",
        "SELECT * FROM t INTO TEMP TABLE u",
        "SELECT * FROM t INTO TEMPORARY TABLE u",
        "WITH x AS (SELECT 1 AS n) SELECT * FROM x INTO TABLE y",
        "select id from customers\ninto\ttable attacker_copy",
        "WITH x AS (SELECT 1 AS n)/**/DELETE FROM t",
        "WITH x AS (SELECT 1 AS n)/**/UPDATE t SET a=1",
        "WITH x AS (SELECT 1 AS n)/**/DROP TABLE t",
        "WITH x AS (SELECT 1 AS n)/**/INSERT INTO t VALUES (1)",
    ],
)
def test_snowflake_rejects_mutating_sql(statement: str) -> None:
    with pytest.raises(HedronError) as exc:
        SnowflakeDataSource(connection_factory=_Conn, statement=statement)
    assert exc.value.diagnostic.code == "HED-DATA-0061"


def test_assert_select_only_allows_with() -> None:
    cleaned = assert_select_only("WITH x AS (SELECT 1 AS n) SELECT * FROM x")
    assert cleaned.lower().startswith("with")


def test_assert_select_only_allows_into_inside_string_literal() -> None:
    cleaned = assert_select_only("SELECT ' into TABLE ' AS note, id FROM customers")
    assert "into" in cleaned.lower()


@pytest.mark.parametrize(
    "statement",
    [
        "SELECT 'a;b' AS marker",
        'SELECT "a;b" AS marker',
        "SELECT $$a;b$$ AS marker",
        "SELECT $tag$a;b$tag$ AS marker",
        "SELECT 'it''s; fine' AS marker",
    ],
)
def test_assert_select_only_allows_semicolon_inside_literals(statement: str) -> None:
    """#108: semicolons inside quoted/dollar-quoted literals are not multi-statement."""
    cleaned = assert_select_only(statement)
    assert cleaned.lower().startswith("select")


def test_assert_select_only_still_rejects_real_multi_statement() -> None:
    with pytest.raises(HedronError) as exc:
        assert_select_only("SELECT 1; SELECT 2")
    assert exc.value.diagnostic.code == "HED-DATA-0061"
