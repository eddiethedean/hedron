"""Minimal runnable source for the Hedron Showcase docs demo.

The complete showcase lives in ``examples/showcase/app.py``; this source keeps
the docs Demo/Code inventory honest without coupling the simulator to a server.
"""

from examples.showcase.app import app

__all__ = ["app"]
