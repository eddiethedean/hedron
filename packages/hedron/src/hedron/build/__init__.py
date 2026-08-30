"""Build orchestration: compile CSS/assets into a versioned manifest."""

from __future__ import annotations

from hedron.build.compile import BuildResult as BuildResult
from hedron.build.compile import run_build as run_build
from hedron.build.fingerprint import relink_fingerprinted_modules
from hedron.build.manifest import load_build_manifest as load_build_manifest
from hedron.build.rewrite import rewrite_module_imports

_relink_fingerprinted_modules = relink_fingerprinted_modules
_rewrite_module_imports = rewrite_module_imports

__all__ = ["BuildResult", "load_build_manifest", "run_build"]
