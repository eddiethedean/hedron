#!/usr/bin/env python3
"""Check external Markdown links; intended for scheduled CI, not every PR."""

from __future__ import annotations

import argparse
import concurrent.futures
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL_PATTERN = re.compile(r"https?://[^\s<>\]\[\"'–—]+")
PLACEHOLDER_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}
EXCLUDED_DOC_ROOTS = {"acceptance", "archive", "implementation", "overrides", "rfcs"}
EXCLUDED_DOCS = {
    "ACCESSIBILITY_FEATURE_RESEARCH.md",
    "DIAGNOSTICS.md",
    "DJANGO_ADAPTER_RESEARCH.md",
    "ENGINEERING_BASELINE.md",
    "FLASK_ADAPTER_RESEARCH.md",
    "GRADIO_FEATURE_CROSSCHECK.md",
    "HTMX_2_AUDIT.md",
    "HTMX_2_EXTENSIONS.md",
    "INFERENCE_OVERRIDES.md",
    "NICEGUI_FEATURE_CROSSCHECK.md",
    "PLOTLY_DASH_FEATURE_CROSSCHECK.md",
    "READINESS_REPORT.md",
    "ROADMAP.md",
    "SPECIFICATION.md",
    "STATUS.md",
    "STREAMLIT_EXTRAS_FEATURE_CROSSCHECK.md",
    "STREAMLIT_FEATURE_CROSSCHECK.md",
    "TRACEABILITY.md",
    "guides/feature-research.md",
}


def extract_urls(text: str) -> set[str]:
    urls: set[str] = set()
    for match in URL_PATTERN.finditer(text):
        url = match.group(0).rstrip(".,;:!?)}`*–—")
        parsed = urllib.parse.urlparse(url)
        host = (parsed.hostname or "").lower()
        if (
            not host
            or host in PLACEHOLDER_HOSTS
            or host.startswith("example.")
            or ".example." in host
            or host.endswith((".example", ".invalid", ".test"))
        ):
            continue
        urls.add(url)
    return urls


def documentation_urls() -> dict[str, list[Path]]:
    files = [ROOT / "README.md", ROOT / "CONTRIBUTING.md", ROOT / "SECURITY.md"]
    files.extend((ROOT / "docs").rglob("*.md"))
    files.extend((ROOT / "packages").glob("*/README.md"))
    found: dict[str, list[Path]] = {}
    for path in files:
        if not path.is_file() or path.is_symlink():
            continue
        if path.is_relative_to(ROOT / "docs"):
            relative_doc = path.relative_to(ROOT / "docs").as_posix()
            if relative_doc.split("/", 1)[0] in EXCLUDED_DOC_ROOTS:
                continue
            if relative_doc in EXCLUDED_DOCS:
                continue
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        for url in extract_urls(text):
            parsed = urllib.parse.urlparse(url)
            match = re.fullmatch(r"/eddiethedean/hedron/(?:blob|tree)/main/(.+)", parsed.path)
            if (
                parsed.hostname == "github.com"
                and match
                and (ROOT / urllib.parse.unquote(match.group(1))).exists()
            ):
                # A link added by the current PR cannot exist on remote main yet. Its
                # checked-out target is the stronger pre-merge assertion.
                continue
            found.setdefault(url, []).append(path.relative_to(ROOT))
    return found


def check_url(url: str, timeout: float) -> tuple[str, str | None]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "hedron-docs-link-check/1.0 (+https://github.com/eddiethedean/hedron)",
            "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
            "Range": "bytes=0-1023",
        },
        method="GET",
    )
    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status = response.status
        except urllib.error.HTTPError as exc:
            status = exc.code
            # Authentication, bot protection, and rate limits still prove the host/path
            # responded. Missing or gone resources are the actionable link failures.
            if status in {401, 403, 405, 429}:
                return url, None
            return url, f"HTTP {status}"
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if attempt == 0:
                continue
            return url, f"{type(exc).__name__}: {exc}"
        break
    if status >= 400:
        return url, f"HTTP {status}"
    return url, None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()

    sources = documentation_urls()
    failures: list[tuple[str, str]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(check_url, url, args.timeout): url for url in sorted(sources)}
        for future in concurrent.futures.as_completed(futures):
            url, problem = future.result()
            if problem:
                failures.append((url, problem))

    if failures:
        lines = ["external documentation links failed:"]
        for url, problem in sorted(failures):
            locations = ", ".join(str(path) for path in sources[url][:3])
            lines.append(f"  {problem}: {url} ({locations})")
        raise SystemExit("\n".join(lines))
    print(f"ok: {len(sources)} external documentation links responded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
