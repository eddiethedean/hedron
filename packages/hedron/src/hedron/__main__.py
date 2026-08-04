"""Allow ``python -m hedron`` as a PATH-independent CLI entry point."""

from __future__ import annotations

from hedron.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
