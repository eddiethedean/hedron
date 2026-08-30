"""Immutable raw-markup value created only at an explicit trust boundary."""

from __future__ import annotations

from hedron_core.diagnostics import error


class TrustedHtml:
    """Immutable raw-markup value created only at an explicit trust boundary."""

    __slots__ = ("_value", "_source")
    _value: str
    _source: str

    def __init__(self, *args: object, **kwargs: object) -> None:
        raise TypeError("TrustedHtml has no public constructor; use TrustedHtml.reviewed(...)")

    @classmethod
    def reviewed(cls, value: object, *, source: object) -> TrustedHtml:
        if not isinstance(value, str):
            raise TypeError("TrustedHtml value must be a string")
        if not isinstance(source, str) or not source:
            raise TypeError("TrustedHtml source must be a non-empty string")
        obj = object.__new__(cls)
        object.__setattr__(obj, "_value", value)
        object.__setattr__(obj, "_source", source)
        return obj

    @classmethod
    def nh3(cls, value: object, *, tags: set[str] | None = None) -> TrustedHtml:
        """Sanitize HTML with nh3 and record policy provenance.

        Requires the optional ``nh3`` dependency (``pip install "hedron[sanitize]"``
        or ``pip install "hedron[markdown]"``).
        """
        if not isinstance(value, str):
            raise TypeError("TrustedHtml value must be a string")
        try:
            import nh3
        except ImportError as exc:  # pragma: no cover - exercised when extra missing
            raise error(
                "HED-SEC-0020",
                title="nh3 sanitizer not installed",
                explanation="TrustedHtml.nh3 requires the nh3 package.",
                remediation='Install with: pip install "hedron[sanitize]" or pip install nh3',
            ) from exc
        cleaned = nh3.clean(value, tags=tags) if tags is not None else nh3.clean(value)
        version = getattr(nh3, "__version__", "unknown")
        return cls.reviewed(cleaned, source=f"nh3:{version}")

    @property
    def value(self) -> str:
        return self._value

    @property
    def source(self) -> str:
        return self._source

    def __str__(self) -> str:
        return f"TrustedHtml(source={self.source!r})"

    def __repr__(self) -> str:
        return f"TrustedHtml.reviewed(..., source={self.source!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TrustedHtml):
            return NotImplemented
        return self.value == other.value and self.source == other.source

    def __hash__(self) -> int:
        return hash(("TrustedHtml", self.value, self.source))
