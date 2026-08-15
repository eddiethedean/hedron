"""Allow ``python -m hedron.cli`` after the module-to-package split."""

from __future__ import annotations

from hedron.cli import main

if __name__ == "__main__":
    main()
