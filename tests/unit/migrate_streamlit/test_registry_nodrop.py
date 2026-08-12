"""Registry no-drop: every Supported catalog symbol has a disposition."""

from __future__ import annotations

from hedron.migrate.ir import Disposition
from hedron.migrate.registry import all_rules, supported_symbols


def test_supported_symbols_nonempty() -> None:
    assert len(supported_symbols()) >= 40


def test_every_rule_has_disposition() -> None:
    for symbol, rule in all_rules().items():
        assert rule.disposition in Disposition
        assert rule.hedron_hint
        assert symbol.startswith("st.")


def test_no_drop_corpus_covers_rfc_subset() -> None:
    required = {
        "st.title",
        "st.header",
        "st.subheader",
        "st.markdown",
        "st.sidebar",
        "st.columns",
        "st.selectbox",
        "st.slider",
        "st.form",
        "st.metric",
        "st.dataframe",
        "st.line_chart",
        "st.cache_data",
        "st.session_state",
        "st.rerun",
    }
    assert required <= supported_symbols()


def test_catalog_matches_supported_symbols_toml() -> None:
    import tomllib
    from pathlib import Path

    data = Path(__file__).resolve().parents[3] / (
        "packages/hedron/src/hedron/migrate/registry/data/supported_symbols.toml"
    )
    payload = tomllib.loads(data.read_text(encoding="utf-8"))
    assert set(payload["symbols"]) == supported_symbols()
