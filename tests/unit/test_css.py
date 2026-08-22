"""Phase 0.3 scoped CSS compiler tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from hedron_core import HedronError, compile_css, scoped_identifier, styles_from_manifest


def test_css_scoping_deterministic() -> None:
    source = """
.root { color: red; }
.root .title { font-weight: bold; }
@keyframes pop { from { opacity: 0; } to { opacity: 1; } }
.animated { animation: pop 200ms; }
"""
    a = compile_css(source, component_id="app:demo.Card")
    b = compile_css(source, component_id="app:demo.Card")
    assert a.manifest.symbols == b.manifest.symbols
    assert a.css == b.css
    assert "h-root-" in a.manifest.symbols["root"]
    assert a.manifest.symbols["root"] in a.css
    assert a.manifest.keyframes["pop"] in a.css


def test_css_global_escape() -> None:
    source = ":global(body) { margin: 0; } .local { color: blue; }"
    result = compile_css(source, component_id="app:x.Y")
    assert "body {" in result.css or "body{" in result.css.replace(" ", "")
    assert result.manifest.symbols["local"] in result.css


def test_css_rejects_remote_and_traversal(tmp_path: Path) -> None:
    with pytest.raises(HedronError) as remote:
        compile_css(
            ".x { background: url(https://evil.example/a.png); }",
            component_id="app:x",
        )
    assert remote.value.diagnostic.code == "HED-CSS-0005"

    root = tmp_path / "comp"
    root.mkdir()
    with pytest.raises(HedronError) as trav:
        compile_css(
            '.x { background: url("../secret.png"); }',
            component_id="app:x",
            registered_roots=[root],
            component_dir=root,
        )
    assert trav.value.diagnostic.code == "HED-ASSET-0002"

    with pytest.raises(HedronError) as abs_url:
        compile_css(
            ".x { background: url(/etc/passwd); }",
            component_id="app:x",
            registered_roots=[root],
            component_dir=root,
        )
    assert abs_url.value.diagnostic.code == "HED-ASSET-0002"

    with pytest.raises(HedronError) as empty_roots:
        compile_css(
            ".x { background: url(icon.png); }",
            component_id="app:x",
            registered_roots=[],
            component_dir=root,
        )
    assert empty_roots.value.diagnostic.code == "HED-ASSET-0002"


def test_css_unknown_style_symbol() -> None:
    styles = styles_from_manifest({"root": "h-root-abc"}, component_id="app:x")
    assert styles.root == "h-root-abc"
    with pytest.raises(HedronError) as exc:
        _ = styles.missing
    assert exc.value.diagnostic.code == "HED-CSS-0003"


def test_scoped_identifier_stable_across_paths() -> None:
    a = scoped_identifier("dist:mod.Name", "root")
    b = scoped_identifier("dist:mod.Name", "root")
    assert a == b


def test_css_v2_does_not_discover_import_extensions_or_rewrite_literals() -> None:
    result = compile_css(
        '@import "theme.css";\n'
        "/* .comment must remain */\n"
        '.root:where(.title) { content: ".literal"; background: url(data:image/svg+xml,.svg); }',
        component_id="app:imports",
    )
    assert "css" not in result.manifest.symbols
    assert "svg" not in result.manifest.symbols
    assert '@import "theme.css";' in result.css
    assert "/* .comment must remain */" in result.css
    assert 'content: ".literal"' in result.css
    assert result.manifest.symbols["root"] in result.css
    assert result.manifest.symbols["title"] in result.css
    assert result.manifest.format_version == 2


def test_css_v2_rewrites_animation_names_grammar_aware() -> None:
    result = compile_css(
        "@keyframes fade { from { opacity: 0; } to { opacity: 1; } }\n"
        ".root { animation: fade 200ms ease-in, other 1s; }",
        component_id="app:animation",
    )
    scoped = result.manifest.keyframes["fade"]
    assert f"animation: {scoped} 200ms ease-in, other 1s" in result.css


def test_v1_css_symbol_manifest_remains_readable() -> None:
    from hedron_core.manifests import CssSymbolManifest

    CssSymbolManifest(
        format_version=1,
        component_id="app:v1",
        symbols={"root": "h-root-legacy"},
        keyframes={},
    ).validate_format()
