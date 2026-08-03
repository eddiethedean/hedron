"""Deploy topology evidence for OPS-002."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "examples" / "reference-app"


def test_compose_and_dockerfile_present() -> None:
    dockerfile = (REF / "Dockerfile").read_text(encoding="utf-8")
    compose = (REF / "docker-compose.yml").read_text(encoding="utf-8")
    caddy = (REF / "Caddyfile").read_text(encoding="utf-8")
    assert "--workers" in dockerfile
    assert "redis" in compose
    assert "/hedron" in caddy
    assert "static" in compose
