"""CLI command: optional native acceleration status."""

from __future__ import annotations

import argparse


def _cmd_accel_status(args: argparse.Namespace) -> int:
    """Report optional native acceleration status."""
    try:
        from hedron_native import __version__ as native_version
        from hedron_native import native_available, native_disabled_by_env
    except ImportError:
        print("hedron-native: not installed (pure-Python serializer active)")
        return 0
    if native_disabled_by_env():
        print(
            f"hedron-native {native_version}: disabled "
            "(HEDRON_NATIVE_DISABLE; pure-Python serializer active)"
        )
        return 0
    status = "loaded" if native_available() else "installed (fallback pure-Python)"
    print(f"hedron-native {native_version}: {status}")
    return 0


cmd_accel_status = _cmd_accel_status
