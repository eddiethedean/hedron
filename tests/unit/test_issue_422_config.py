"""#422: diagnostic_severities config key."""

from pathlib import Path

from hedron.config import load_hedron_settings


def test_diagnostic_severities_is_a_known_key(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[tool.hedron]\nformat_version = 1\ndiagnostic_severities = { "HED-TEST-0001" = "warning" }\n',
        encoding="utf-8",
    )
    settings = load_hedron_settings(pyproject)
    assert settings.diagnostic_severities == {"HED-TEST-0001": "warning"}
