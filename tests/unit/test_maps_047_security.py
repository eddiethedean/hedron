"""SECURITY-047 origin/style/proxy/popup/geojson."""

from __future__ import annotations

import pytest

from hedron_core import HedronError, RenderMode, render
from hedron_core.codes import HED_MAP_POLICY_0002, HED_MAP_STYLE_0001
from hedron_maps import Map, MapPolicy, MapStyle, VectorTiles, compile_map
from hedron_maps.proxy import assert_ssrf_safe
from hedron_maps.spec import AccessibilityDef, MapSpec, RasterTiles


def test_unsafe_style_keys() -> None:
    with pytest.raises(HedronError) as exc:
        compile_map(
            MapSpec(
                basemap=VectorTiles(
                    url="https://tiles.example.com/{z}/{x}/{y}.pbf",
                    attribution="x",
                    style=MapStyle(sources={"__proto__": {"type": "vector"}}),
                ),
                policy=MapPolicy(allowed_origins=("https://tiles.example.com",)),
                accessibility=AccessibilityDef(title="T", description="D"),
            )
        )
    assert exc.value.diagnostic.code in {HED_MAP_STYLE_0001, "HED-MAP-SPEC-0001"}


def test_javascript_scheme_rejected() -> None:
    with pytest.raises(HedronError) as exc:
        compile_map(
            MapSpec(
                basemap=RasterTiles(url="javascript:alert(1)//{z}/{x}/{y}", attribution="x"),
                accessibility=AccessibilityDef(title="T", description="D"),
            )
        )
    assert exc.value.diagnostic.code == HED_MAP_POLICY_0002


def test_proxy_blocks_loopback() -> None:
    policy = MapPolicy(allowed_origins=("https://127.0.0.1",))
    with pytest.raises(HedronError):
        assert_ssrf_safe("https://127.0.0.1/tiles", policy, resolve_dns=False)


def test_proxy_rejects_malformed_ports_and_brackets() -> None:
    policy = MapPolicy(
        remote_requests_permitted=True,
        allowed_origins=("https://example.com",),
    )
    for raw in (
        "https://example.com:abc/tiles",
        "https://example.com:99999/tiles",
        "https://[::1/tiles",
    ):
        with pytest.raises(HedronError):
            assert_ssrf_safe(raw, policy, resolve_dns=False)


def test_compile_rejects_malformed_ports_and_brackets() -> None:
    for raw in (
        "https://example.com:abc/{z}/{x}/{y}",
        "https://example.com:99999/{z}/{x}/{y}",
        "https://[::1/{z}/{x}/{y}",
    ):
        with pytest.raises(HedronError):
            compile_map(
                MapSpec(
                    basemap=RasterTiles(url=raw, attribution="x"),
                    accessibility=AccessibilityDef(title="T", description="D"),
                )
            )


def test_threat_review_packet_present() -> None:
    from pathlib import Path

    root = Path("docs/acceptance/security-review-047")
    assert (root / "BRIEF.md").is_file()
    assert (root / "DISPOSITION.toml").is_file()
    assert (root / "REDACTED_REPORT.md").is_file()
    assert "open_critical = 0" in (root / "DISPOSITION.toml").read_text(encoding="utf-8")
    html = render(
        Map(
            center=(1.0, 2.0),
            title="Safe",
            description="Sanitize",
            geojson={
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {"name": "Safe Place", "html": "<script>alert(1)</script>"},
                        "geometry": {"type": "Point", "coordinates": [2.0, 1.0]},
                    }
                ],
            },
        ),
        mode=RenderMode.FRAGMENT,
    ).html
    assert "<script>" not in html
    assert "Safe Place" in html


def test_style_source_data_and_javascript_rejected() -> None:
    from hedron_core.codes import HED_MAP_POLICY_0001

    with pytest.raises(HedronError) as remote:
        compile_map(
            MapSpec(
                basemap=VectorTiles(
                    url="https://tiles.example.com/{z}/{x}/{y}.pbf",
                    attribution="x",
                    style=MapStyle(
                        sources={
                            "ok": {
                                "type": "vector",
                                "tiles": ["https://tiles.example.com/{z}/{x}/{y}.pbf"],
                            },
                            "exfil": {"type": "geojson", "data": "https://evil.example/steal.json"},
                        },
                        layers=[{"id": "bg", "type": "background"}],
                    ),
                ),
                policy=MapPolicy(allowed_origins=("https://tiles.example.com",)),
                accessibility=AccessibilityDef(title="T", description="D"),
            )
        )
    assert remote.value.diagnostic.code == HED_MAP_POLICY_0001
    with pytest.raises(HedronError) as js:
        compile_map(
            MapSpec(
                basemap=VectorTiles(
                    url="https://tiles.example.com/{z}/{x}/{y}.pbf",
                    attribution="x",
                    style=MapStyle(
                        sources={"js": {"type": "geojson", "data": "javascript:alert(1)"}},
                        layers=[{"id": "bg", "type": "background"}],
                    ),
                ),
                policy=MapPolicy(allowed_origins=("https://tiles.example.com",)),
                accessibility=AccessibilityDef(title="T", description="D"),
            )
        )
    assert js.value.diagnostic.code == HED_MAP_POLICY_0002
