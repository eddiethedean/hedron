"""Robust coverage for example/tutorial docs sims added for 0.19 demos."""

from __future__ import annotations

import ast
import importlib.util
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"

# New / multi-sim example pages from the runnable + tutorial demo pass.
_EXAMPLE_EXPECTED_SIMS: dict[str, frozenset[str]] = {
    "examples/notes-sqlalchemy.md": frozenset({"crud-notes"}),
    "examples/session-auth.md": frozenset({"auth-login"}),
    "examples/file-upload.md": frozenset({"file-upload"}),
    "examples/jobs-poll.md": frozenset({"jobs-poll"}),
    "examples/single-file.md": frozenset({"hello-refresh"}),
    "examples/crud-tutorial.md": frozenset({"minimal-form", "mutations-htmx", "crud-notes"}),
    # The reference app uses HTTP Basic. Session-form auth is demonstrated only by
    # examples/session-auth, so embedding auth-login here would teach the wrong credentials.
    "examples/reference-app.md": frozenset({"csrf-guard", "crud-notes", "charts-htmx"}),
}


@pytest.fixture(scope="module", autouse=True)
def _docs_on_path() -> None:
    path = str(DOCS)
    if path not in sys.path:
        sys.path.insert(0, path)


def _route_payload(html_out: str) -> dict:
    match = re.search(
        r"<(?:template|script)[^>]*data-hedron-sim-routes[^>]*>(.*?)</(?:template|script)>",
        html_out,
        flags=re.DOTALL,
    )
    assert match is not None, "missing route table JSON"
    raw = match.group(1).replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return json.loads(raw.replace("\\u003c", "<"))


def _load_guide_tabs() -> tuple[tuple[str, str, str], ...]:
    path = ROOT / "scripts" / "sync_demo_code_tabs.py"
    spec = importlib.util.spec_from_file_location("sync_demo_code_tabs", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.GUIDE_TABS


@pytest.mark.usefixtures("_docs_on_path")
def test_file_upload_demo_routes_and_status_codes() -> None:
    from demos.guides import build_file_upload_demo

    html_out = build_file_upload_demo()
    assert 'data-hedron-sim="file-upload"' in html_out
    assert "Upload roster.txt" in html_out
    assert "Upload malware.exe" in html_out
    assert 'hx-post="/upload-ok"' in html_out
    assert 'hx-post="/upload-bad"' in html_out
    assert 'hx-target="#upload-stage"' in html_out
    # Docs sim must not use a native multipart form that could POST to the docs host.
    assert "<form" not in html_out.lower() or 'enctype="multipart' not in html_out.lower()

    payload = _route_payload(html_out)
    assert payload["demoId"] == "file-upload"
    routes = payload["routes"]
    assert set(routes) == {"POST /upload-ok", "POST /upload-bad", "GET /reset"}

    ok = routes["POST /upload-ok"]
    assert ok["status"] == 200
    assert ok["regions"][0]["selector"] == "#upload-stage"
    assert "Received roster.txt" in ok["html"]
    assert "name,role" in ok["html"]
    assert "Upload another" in ok["html"]
    assert 'hx-get="/reset"' in ok["html"]

    bad = routes["POST /upload-bad"]
    assert bad["status"] == 422
    assert "Rejected type: malware.exe" in bad["html"]
    assert "Back to upload" in bad["html"]
    assert "Received roster.txt" not in bad["html"]

    reset = routes["GET /reset"]
    assert reset["status"] == 200
    assert "Upload roster.txt" in reset["html"]
    assert "Upload malware.exe" in reset["html"]


@pytest.mark.parametrize(
    "relative_path",
    ("examples/showcase/app.py", "examples/edron-showcase/app.py"),
)
def test_real_showcases_declare_light_and_dark_theme_modes(relative_path: str) -> None:
    path = ROOT / relative_path
    module_name = "showcase_theme_" + path.parent.name.replace("-", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    theme = module.THEME
    resolved = theme.to_theme() if hasattr(theme, "to_theme") else theme
    assert "dark" in resolved.modes


@pytest.mark.parametrize(
    ("relative_path", "source_path", "sim_id"),
    (
        ("examples/showcase.md", "examples/showcase/app.py", "showcase-dashboard"),
        (
            "examples/edron-showcase.md",
            "examples/edron-showcase/app.py",
            "edron-showcase-dashboard",
        ),
    ),
)
def test_showcase_docs_point_to_real_source_not_simulators(
    relative_path: str,
    source_path: str,
    sim_id: str,
) -> None:
    text = (DOCS / relative_path).read_text(encoding="utf-8")
    assert source_path in text
    if sim_id == "edron-showcase-dashboard":
        assert "<!-- hedron-sim:edron-showcase -->" in text
        assert "edron-sim" in text
    else:
        assert sim_id not in text
        assert "documentation-only showcase implementation" in text


@pytest.mark.usefixtures("_docs_on_path")
def test_file_upload_contract_covers_reject_reset_accept() -> None:
    from demos.contracts import CONTRACTS

    contract = next(c for c in CONTRACTS if c.id == "file-upload")
    assert contract.min_steps >= 3
    labels = []
    for step in contract.steps:
        assert step.click
        if 'has-text("' in step.click:
            labels.append(step.click.split('has-text("', 1)[1].rsplit('")', 1)[0])
    assert "Upload malware.exe" in labels
    assert "Back to upload" in labels
    assert "Upload roster.txt" in labels
    traces = [s.expect_trace for s in contract.steps if s.expect_trace]
    assert any("422" in t for t in traces)
    assert any("upload-ok" in t or "200" in t for t in traces)
    assert any("reset" in t for t in traces)


@pytest.mark.usefixtures("_docs_on_path")
def test_file_upload_runnable_is_importable_real_hedron_app() -> None:
    from demos.runnable_code import runnable_path, runnable_source

    path = runnable_path("file-upload")
    assert path.is_file()
    source = runnable_source("file-upload")
    assert "FileUpload" in source
    assert "multipart/form-data" in source
    assert ".txt" in source and ".csv" in source
    assert "csrf_token" in source
    # Structural: defines a Hedron app + upload action (no SimApp).
    tree = ast.parse(source)
    names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert "home" in names
    assert "upload" in names
    assert "SimApp" not in source
    assert "from hedron import" in source or "import hedron" in source


@pytest.mark.usefixtures("_docs_on_path")
def test_example_pages_embed_expected_sims() -> None:
    guide_tabs = _load_guide_tabs()
    by_page: dict[str, set[str]] = defaultdict(set)
    for rel, sim_id, _blurb in guide_tabs:
        if rel.startswith("examples/"):
            by_page[rel].add(sim_id)

    for rel, expected in _EXAMPLE_EXPECTED_SIMS.items():
        assert expected <= by_page[rel], (
            f"{rel}: GUIDE_TABS missing {sorted(expected - by_page[rel])}"
        )
        text = (DOCS / rel).read_text(encoding="utf-8")
        for sim_id in expected:
            marker = f"<!-- hedron-sim:{sim_id} -->"
            assert marker in text, f"{rel} missing {marker}"
            # Each sim sits in its own Demo tab, followed by a Code tab with app.py.
            idx = text.index(marker)
            before = text[max(0, idx - 400) : idx]
            after = text[idx : idx + 800]
            assert '=== "Demo"' in before or '=== "Demo"' in text[max(0, idx - 800) : idx], (
                f"{rel}: {sim_id} not under a Demo tab"
            )
            assert '=== "Code"' in after, f"{rel}: {sim_id} missing following Code tab"
            assert "```python" in after, f"{rel}: {sim_id} Code tab missing python fence"
            assert "app.py" in after, f"{rel}: {sim_id} Code tab missing app.py title"


@pytest.mark.usefixtures("_docs_on_path")
def test_tutorial_pages_have_distinct_multi_sim_sections() -> None:
    """CRUD + reference-app tutorials must not collapse multiple sims into one tab."""
    crud = (DOCS / "examples/crud-tutorial.md").read_text(encoding="utf-8")
    assert crud.count('=== "Demo"') >= 3
    assert crud.count("<!-- hedron-sim:minimal-form -->") == 1
    assert crud.count("<!-- hedron-sim:mutations-htmx -->") == 1
    assert crud.count("<!-- hedron-sim:crud-notes -->") == 1

    ref = (DOCS / "examples/reference-app.md").read_text(encoding="utf-8")
    assert ref.count('=== "Demo"') >= 3
    for sim_id in ("csrf-guard", "crud-notes", "charts-htmx"):
        assert ref.count(f"<!-- hedron-sim:{sim_id} -->") == 1


@pytest.mark.usefixtures("_docs_on_path")
@pytest.mark.parametrize(
    ("builder_name", "demo_id", "required_routes"),
    [
        (
            "build_file_upload_demo",
            "file-upload",
            {"POST /upload-ok", "POST /upload-bad", "GET /reset"},
        ),
        ("build_crud_demo", "crud-notes", {"POST /notes", "DELETE /notes/item"}),
        ("build_auth_login_demo", "auth-login", {"POST /login"}),
        ("build_jobs_poll_demo", "jobs-poll", {"GET /jobs/42"}),
        ("build_csrf_guard_demo", "csrf-guard", {"POST /do", "POST /do-missing"}),
        ("build_charts_htmx_demo", "charts-htmx", {"GET /charts/refresh"}),
        ("build_minimal_form_demo", "minimal-form", {"POST /save"}),
        ("build_mutations_htmx_demo", "mutations-htmx", {"POST /save"}),
    ],
)
def test_new_example_demo_builders_emit_stable_islands(
    builder_name: str,
    demo_id: str,
    required_routes: set[str],
) -> None:
    from demos import guides

    builder = getattr(guides, builder_name)
    html_out = builder()
    assert f'data-hedron-sim="{demo_id}"' in html_out
    assert "data-hedron-sim-routes" in html_out
    assert "data-hedron-sim-trace" in html_out
    payload = _route_payload(html_out)
    assert payload["demoId"] == demo_id
    missing = required_routes - set(payload["routes"])
    assert not missing, f"{demo_id} missing routes {sorted(missing)}"
    for key, route in payload["routes"].items():
        assert "html" in route, key
        assert isinstance(route.get("status"), int), key
        assert route.get("regions"), key


@pytest.mark.usefixtures("_docs_on_path")
def test_file_upload_include_matches_builder() -> None:
    from demos.guides import build_file_upload_demo

    built = build_file_upload_demo().strip() + "\n"
    on_disk = (DOCS / "includes/sim/file-upload.html").read_text(encoding="utf-8")
    assert built == on_disk


def _hx_method_path(markup: str) -> tuple[str, str] | None:
    for attr, method in (
        ("hx-post", "POST"),
        ("hx-delete", "DELETE"),
        ("hx-put", "PUT"),
        ("hx-patch", "PATCH"),
        ("hx-get", "GET"),
    ):
        found = re.search(rf'{attr}="([^"]+)"', markup)
        if found:
            return method, found.group(1)
    return None


def _button_or_form_hx(current: str, label: str) -> tuple[str, str]:
    """Resolve hx-* from the labeled button, or its enclosing form."""
    btn_match = re.search(
        rf"<button\b[^>]*>(?:(?!</button>).)*{re.escape(label)}(?:(?!</button>).)*</button>",
        current,
        flags=re.I | re.S,
    )
    assert btn_match is not None, f"no <button> for {label!r}"
    btn = btn_match.group(0)
    resolved = _hx_method_path(btn)
    if resolved:
        return resolved
    # Submit buttons inherit hx from the nearest preceding open <form …>.
    before = current[: btn_match.start()]
    forms = list(re.finditer(r"<form\b[^>]*>", before, flags=re.I))
    assert forms, f"no enclosing form for submit {label!r}"
    form_tag = forms[-1].group(0)
    resolved = _hx_method_path(form_tag)
    assert resolved, f"no hx-* on form for {label!r}"
    return resolved


@pytest.mark.usefixtures("_docs_on_path")
@pytest.mark.parametrize("sim_id", ["file-upload", "csrf-guard", "hello-refresh"])
def test_new_example_demos_offline_route_walk(sim_id: str) -> None:
    """Full contract walk for demos whose route table is static (no form variants)."""
    from demos.contracts import CONTRACTS

    contract = next(c for c in CONTRACTS if c.id == sim_id)
    html_out = contract.builder()
    payload = _route_payload(html_out)
    current = html_out
    routes = payload["routes"]

    for index, step in enumerate(contract.steps):
        if not step.click or step.auto:
            continue
        assert 'has-text("' in step.click, f"{sim_id} step[{index}]: {step.click!r}"
        label = step.click.split('has-text("', 1)[1].rsplit('")', 1)[0]
        assert label in current, f"{sim_id} step[{index}]: {label!r} missing in current HTML"
        method, path = _button_or_form_hx(current, label)
        key = f"{method} {path}"
        assert key in routes, f"{sim_id} step[{index}]: missing route {key}"
        route = routes[key]
        if step.expect_trace:
            status_ok = str(route["status"]) in step.expect_trace
            method_ok = key.split()[0] in step.expect_trace
            assert status_ok or method_ok, (
                f"{sim_id} step[{index}]: trace mismatch {route['status']} vs {step.expect_trace}"
            )
        body = route["html"]
        needles = tuple(n for n in (step.contains, *step.contains_all) if n)
        for needle in needles:
            assert needle in body, f"{sim_id} step[{index}]: {needle!r} not in route HTML"
        if step.not_contains:
            assert step.not_contains not in body, (
                f"{sim_id} step[{index}]: unexpected {step.not_contains!r}"
            )
        region_id = route["regions"][0]["id"]
        region_re = re.compile(
            rf'<(?:div|section|article|form|ul|ol|li)\b[^>]*\bid="{re.escape(region_id)}"[^>]*>'
            rf".*?"
            rf"</(?:div|section|article|form|ul|ol|li)>",
            flags=re.S,
        )
        current = region_re.sub(body, current, count=1) if region_re.search(current) else body


@pytest.mark.usefixtures("_docs_on_path")
@pytest.mark.parametrize(
    "sim_id",
    ["auth-login", "minimal-form", "mutations-htmx", "crud-notes", "jobs-poll", "charts-htmx"],
)
def test_form_and_sequence_demos_first_click_route(sim_id: str) -> None:
    """Form-variant / sequence demos: first click resolves to a canned route key."""
    from demos.contracts import CONTRACTS

    contract = next(c for c in CONTRACTS if c.id == sim_id)
    html_out = contract.builder()
    payload = _route_payload(html_out)
    first = next(s for s in contract.steps if s.click and not s.auto)
    assert first.click and 'has-text("' in first.click
    label = first.click.split('has-text("', 1)[1].rsplit('")', 1)[0]
    method, path = _button_or_form_hx(html_out, label)
    key = f"{method} {path}"
    assert key in payload["routes"], f"{sim_id}: missing {key}"
    route = payload["routes"][key]
    assert isinstance(route["status"], int)
    assert route["regions"]
    assert route["html"]


@pytest.mark.usefixtures("_docs_on_path")
def test_guide_tabs_cover_every_example_expected_sim() -> None:
    guide_tabs = _load_guide_tabs()
    listed = {(rel, sim) for rel, sim, _ in guide_tabs}
    for rel, sims in _EXAMPLE_EXPECTED_SIMS.items():
        for sim in sims:
            assert (rel, sim) in listed, f"GUIDE_TABS missing {(rel, sim)}"
