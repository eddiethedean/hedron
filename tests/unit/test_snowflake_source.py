from hedron_data.snowflake_source import SnowflakeDataSource


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
