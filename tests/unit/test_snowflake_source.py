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
    ],
)
def test_snowflake_rejects_mutating_sql(statement: str) -> None:
    with pytest.raises(HedronError):
        SnowflakeDataSource(connection_factory=_Conn, statement=statement)


def test_assert_select_only_allows_with() -> None:
    cleaned = assert_select_only("WITH x AS (SELECT 1 AS n) SELECT * FROM x")
    assert cleaned.lower().startswith("with")
