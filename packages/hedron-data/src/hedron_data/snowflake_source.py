"""Snowflake-backed bounded data source."""

from __future__ import annotations

import importlib
import re
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Generic, TypeVar, cast

from hedron_core.diagnostics import error
from hedron_data.plans import TransformPlan, plan_from_query
from hedron_data.sources import (
    ColumnSchema,
    DataChanges,
    DataPage,
    DataQuery,
    DataSaveResult,
    FieldError,
)

T = TypeVar("T")

__all__ = ["SnowflakeDataSource", "require_snowflake", "assert_select_only"]


def _strip_sql_comments(statement: str) -> str:
    """Remove -- line and /* */ block comments without interpreting string contents deeply."""
    out: list[str] = []
    i = 0
    n = len(statement)
    in_single = False
    in_double = False
    dollar_tag: str | None = None
    while i < n:
        ch = statement[i]
        nxt = statement[i + 1] if i + 1 < n else ""
        if dollar_tag is not None:
            if statement.startswith(dollar_tag, i):
                out.append(dollar_tag)
                i += len(dollar_tag)
                dollar_tag = None
                continue
            out.append(ch)
            i += 1
            continue
        if in_single:
            out.append(ch)
            if ch == "'" and nxt == "'":
                out.append(nxt)
                i += 2
                continue
            if ch == "'":
                in_single = False
            i += 1
            continue
        if in_double:
            out.append(ch)
            if ch == '"' and nxt == '"':
                out.append(nxt)
                i += 2
                continue
            if ch == '"':
                in_double = False
            i += 1
            continue
        if ch == "$":
            tag = _parse_dollar_quote_tag(statement, i)
            if tag is not None:
                dollar_tag = tag
                out.append(tag)
                i += len(tag)
                continue
        if ch == "'":
            in_single = True
            out.append(ch)
            i += 1
            continue
        if ch == '"':
            in_double = True
            out.append(ch)
            i += 1
            continue
        if ch == "-" and nxt == "-":
            i += 2
            while i < n and statement[i] not in "\r\n":
                i += 1
            continue
        if ch == "/" and nxt == "*":
            i += 2
            while i + 1 < n and not (statement[i] == "*" and statement[i + 1] == "/"):
                i += 1
            i = min(i + 2, n)
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _parse_dollar_quote_tag(statement: str, start: int) -> str | None:
    """Return ``$tag$`` / ``$$`` opening tag at ``start``, or ``None`` if not a dollar quote."""
    if start >= len(statement) or statement[start] != "$":
        return None
    j = start + 1
    n = len(statement)
    while j < n and (statement[j].isalnum() or statement[j] == "_"):
        j += 1
    if j < n and statement[j] == "$":
        return statement[start : j + 1]
    return None


def _without_sql_string_literals(statement: str) -> str:
    """Blank quoted SQL string contents so keyword scans ignore literal data."""
    out: list[str] = []
    i = 0
    n = len(statement)
    in_single = False
    in_double = False
    dollar_tag: str | None = None
    while i < n:
        ch = statement[i]
        nxt = statement[i + 1] if i + 1 < n else ""
        if dollar_tag is not None:
            if statement.startswith(dollar_tag, i):
                out.append(" " * len(dollar_tag))
                i += len(dollar_tag)
                dollar_tag = None
                continue
            out.append(" ")
            i += 1
            continue
        if in_single:
            if ch == "'" and nxt == "'":
                out.append("  ")
                i += 2
                continue
            out.append(" ")
            if ch == "'":
                in_single = False
            i += 1
            continue
        if in_double:
            if ch == '"' and nxt == '"':
                out.append("  ")
                i += 2
                continue
            out.append(" ")
            if ch == '"':
                in_double = False
            i += 1
            continue
        if ch == "$":
            tag = _parse_dollar_quote_tag(statement, i)
            if tag is not None:
                dollar_tag = tag
                out.append(" " * len(tag))
                i += len(tag)
                continue
        if ch == "'":
            in_single = True
            out.append(" ")
            i += 1
            continue
        if ch == '"':
            in_double = True
            out.append(" ")
            i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


_INTO_TOKEN = re.compile(r"\binto\b", re.IGNORECASE)
# After comment strip, `)/**/DELETE` becomes `)DELETE` — do not require a space (#572).
_MUTATING_AFTER_PAREN = re.compile(
    r"\)\s*(?:insert|update|delete|merge|drop|alter|create|truncate|call|grant|"
    r"revoke|copy|put|remove|undrop)\b",
    re.IGNORECASE,
)
_MUTATING_STATEMENT_PREFIXES = (
    "insert ",
    "update ",
    "delete ",
    "merge ",
    "drop ",
    "alter ",
    "create ",
    "truncate ",
    "call ",
    "grant ",
    "revoke ",
    "copy ",
    "put ",
    "remove ",
    "undrop ",
)


def assert_select_only(statement: str) -> str:
    """Require a single SELECT/WITH statement; reject mutating or multi-statement SQL."""
    cleaned = _strip_sql_comments(statement).strip().rstrip(";").strip()
    if not cleaned:
        raise error(
            "HED-DATA-0061",
            title="Snowflake statement must be a SELECT",
            explanation="Empty SQL is not accepted through the data source.",
            remediation="Pass a SELECT and apply mutations through an app-owned bridge.",
        )
    # Reject additional statements (semicolons outside strings already stripped of comments).
    lowered = cleaned.lower()
    # Multi-statement guard: semicolon remaining after strip of trailing, outside literals.
    if ";" in _without_sql_string_literals(cleaned):
        raise error(
            "HED-DATA-0061",
            title="Snowflake statement must be a SELECT",
            explanation="Multi-statement SQL is not accepted through the data source.",
            remediation="Pass a single SELECT/WITH statement.",
        )
    first = lowered.lstrip()
    if not (first.startswith("select") or first.startswith("with")):
        raise error(
            "HED-DATA-0061",
            title="Snowflake statement must be a SELECT",
            explanation="Mutating SQL is not accepted through the data source.",
            remediation="Pass a SELECT and apply mutations through an app-owned bridge.",
        )
    # Reject DML/DDL that follows a CTE/paren close, including comment-glued forms (#572).
    scan = _without_sql_string_literals(cleaned)
    compact = " ".join(lowered.split())
    if _MUTATING_AFTER_PAREN.search(scan) or any(
        compact.startswith(bad) for bad in _MUTATING_STATEMENT_PREFIXES
    ):
        raise error(
            "HED-DATA-0061",
            title="Snowflake statement must be a SELECT",
            explanation="Mutating SQL is not accepted through the data source.",
            remediation="Pass a SELECT and apply mutations through an app-owned bridge.",
        )
    # SELECT … INTO [TEMP[ORARY]] TABLE is a mutation in Snowflake (#197).
    if _INTO_TOKEN.search(_without_sql_string_literals(cleaned)):
        raise error(
            "HED-DATA-0061",
            title="Snowflake statement must be a SELECT",
            explanation=(
                "SELECT … INTO table materialization is not accepted through the "
                "SELECT-only data source."
            ),
            remediation="Pass a plain SELECT/WITH and apply mutations through an app-owned bridge.",
        )
    return cleaned


def require_snowflake() -> Any:
    try:
        return importlib.import_module("snowflake.connector")
    except ImportError as exc:
        raise error(
            "HED-DATA-0060",
            title="snowflake extra not installed",
            explanation="SnowflakeDataSource requires snowflake-connector-python.",
            remediation='Install with: pip install "hedron-data[snowflake]"',
        ) from exc


class SnowflakeDataSource(Generic[T]):
    """Execute app-owned parameterized SQL with LIMIT/OFFSET budgets."""

    def __init__(
        self,
        *,
        connection_factory: Callable[[], Any],
        statement: str,
        schema: Sequence[ColumnSchema] = (),
        to_row: Callable[[dict[str, Any]], T] | None = None,
        max_page_size: int = 100,
        params: Sequence[Any] | None = None,
    ) -> None:
        self._statement = assert_select_only(statement)
        self._connection_factory = connection_factory
        self._schema = tuple(schema)
        self._to_row: Callable[[dict[str, Any]], T] = to_row or (lambda r: cast(T, r))
        self._secret_fields = frozenset(
            column.name.casefold() for column in self._schema if column.secret
        )
        self._max_page_size = max_page_size
        self._params = tuple(params or ())

    def plan_for(self, query: DataQuery) -> TransformPlan:
        return plan_from_query(query, max_rows=self._max_page_size)

    def fetch(self, query: DataQuery) -> DataPage[T]:
        q = query.validated(max_page_size=self._max_page_size)
        if q.sort or q.filters or q.search or q.projection:
            raise error(
                "HED-DATA-0061",
                title="Snowflake query refinements not supported",
                explanation=(
                    "SnowflakeDataSource.fetch currently applies LIMIT/OFFSET only; "
                    "sort/filters/search/projection would be silently dropped."
                ),
                remediation=(
                    "Push refinements into the SELECT statement or wait for pushdown support."
                ),
            )
        sql = f"SELECT * FROM ({self._statement}) AS hedron_src LIMIT %s OFFSET %s"
        conn = self._connection_factory()
        try:
            cur = conn.cursor()
            try:
                cur.execute(sql, (*self._params, q.limit, q.offset))
                descriptions = cast(Sequence[Sequence[Any]], cur.description or ())
                colnames: list[str] = [str(col[0]) for col in descriptions]
                raw_rows = cast(Sequence[Sequence[Any]], cur.fetchmany(q.limit))
                rows: list[T] = []
                for row in raw_rows:
                    raw = {
                        colnames[i]: value
                        for i, value in enumerate(row)
                        if colnames[i].casefold() not in self._secret_fields
                    }
                    converted = self._to_row(raw)
                    if isinstance(converted, Mapping):
                        mapping = cast(Mapping[object, object], converted)
                        cleaned: dict[str, Any] = {
                            str(key): value
                            for key, value in mapping.items()
                            if str(key).casefold() not in self._secret_fields
                        }
                        converted = cast(
                            T,
                            cleaned,
                        )
                    rows.append(converted)
                count_sql = f"SELECT COUNT(*) FROM ({self._statement}) AS hedron_src"
                cur.execute(count_sql, self._params)
                count_row = cast(Sequence[Any], cur.fetchone() or (0,))
                total = int(count_row[0])
            finally:
                cur.close()
        finally:
            close = getattr(conn, "close", None)
            if callable(close):
                close()
        return DataPage(
            rows=rows,
            schema=self._schema,
            total=total,
            next_offset=q.offset + q.limit if q.offset + q.limit < total else None,
        )

    def apply(self, changes: DataChanges[T]) -> DataSaveResult[T]:
        return DataSaveResult(
            ok=False,
            errors=(
                FieldError(
                    row_key=None,
                    field=None,
                    message="SnowflakeDataSource.apply requires an app-owned mutation bridge",
                ),
            ),
        )

    def load(self, query: DataQuery) -> DataPage[T]:
        return self.fetch(query)
