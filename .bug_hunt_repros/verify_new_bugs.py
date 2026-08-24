#!/usr/bin/env python3
"""Verify candidate new bugs before GitHub issue creation."""

from __future__ import annotations

import io
import json
import zipfile

print("=" * 70)
print("VERIFY NEW BUG CANDIDATES")
print("=" * 70)

results: list[tuple[str, bool, str]] = []


def record(name: str, confirmed: bool, detail: str) -> None:
    results.append((name, confirmed, detail))
    status = "CONFIRMED" if confirmed else "NOT CONFIRMED"
    print(f"\n[{status}] {name}")
    print(detail)


# ── 1. UploadFlow result route 422 ─────────────────────────────────────
try:
    from fastapi.testclient import TestClient
    from fastapi import Depends
    from hedron import Hedron, Text, UploadFlow
    from hedron.upload import UploadField

    app = Hedron(
        title="up",
        security="development",
        explorer="off",
        session_secret="x" * 32,
    )
    app.include_feature(
        UploadFlow(
            name="docs",
            field=UploadField(),
            authorize=Depends(lambda: None),
            store=lambda h: "stored",
            result=lambda s: Text(f"R:{s}"),
        )
    )
    c = TestClient(app)
    csrf = c.get("/docs/upload").cookies.get("hedron_csrf")
    c.post(
        "/docs/upload",
        data={"csrf_token": csrf},
        files={"file": ("a.txt", b"x", "text/plain")},
    )
    r = c.get("/docs/result", headers={"HX-Request": "true"})
    confirmed = r.status_code == 422 and "query.request" in r.text
    record(
        "UploadFlow result route 422",
        confirmed,
        f"status={r.status_code} body={r.text[:200]!r}",
    )
except Exception as exc:
    record("UploadFlow result route 422", False, f"Error: {exc}")

# ── 2. UploadFlow result missing authorize ───────────────────────────────
try:
    upload_deps = None
    result_deps = None
    for route in app.routes:
        path = getattr(route, "path", "")
        if path == "/docs/upload":
            upload_deps = len(route.dependant.dependencies)
        if path == "/docs/result":
            result_deps = len(route.dependant.dependencies)
    confirmed = upload_deps == 1 and result_deps == 0
    record(
        "UploadFlow result missing authorize",
        confirmed,
        f"upload deps={upload_deps}, result deps={result_deps}",
    )
except Exception as exc:
    record("UploadFlow result missing authorize", False, f"Error: {exc}")

# ── 3. validate_upload_filename NUL sanitization ─────────────────────────
try:
    from hedron.builtins.files import validate_upload_filename
    from hedron_core.uploads import validate_directory_upload

    sanitized = validate_upload_filename("safe\x00evil.txt")
    dir_rejects = False
    try:
        validate_directory_upload([("safe\x00evil.txt", 1)], max_files=10, max_total_size=100)
    except ValueError:
        dir_rejects = True
    confirmed = sanitized == "safe_evil.txt" and dir_rejects
    record(
        "validate_upload_filename NUL sanitization",
        confirmed,
        f"sanitized={sanitized!r}, directory_upload_rejects={dir_rejects}",
    )
except Exception as exc:
    record("validate_upload_filename NUL sanitization", False, f"Error: {exc}")

# ── 4. redact_value Secret in set ────────────────────────────────────────
try:
    from hedron_core.security.secrets import Secret, redact_value, is_secret

    out = redact_value({Secret("leak")})
    confirmed = any(is_secret(x) for x in out)
    record(
        "redact_value Secret in set",
        confirmed,
        f"output={out!r}, live_secret_present={confirmed}",
    )
except Exception as exc:
    record("redact_value Secret in set", False, f"Error: {exc}")

# ── 5. UploadFlow multi-file last wins ───────────────────────────────────
try:
    from hedron.upload import UploadBudget

    calls: list[str] = []
    app2 = Hedron(
        title="up2",
        security="development",
        explorer="off",
        session_secret="y" * 32,
    )
    app2.include_feature(
        UploadFlow(
            name="docs",
            field=UploadField(
                name="file",
                budget=UploadBudget(maximum_size=10000, maximum_count=3),
            ),
            authorize=Depends(lambda: None),
            store=lambda h: calls.append(h.filename) or h.filename,
            result=lambda s: Text(f"stored={s}"),
        )
    )
    c2 = TestClient(app2)
    csrf2 = c2.get("/docs/upload").cookies.get("hedron_csrf")
    r2 = c2.post(
        "/docs/upload",
        data={"csrf_token": csrf2},
        files=[
            ("file", ("a.txt", b"a", "text/plain")),
            ("file", ("b.txt", b"b", "text/plain")),
        ],
    )
    confirmed = calls == ["a.txt", "b.txt"] and r2.text == "<p>stored=b.txt</p>"
    record(
        "UploadFlow multi-file last wins",
        confirmed,
        f"calls={calls}, response={r2.text!r}",
    )
except Exception as exc:
    record("UploadFlow multi-file last wins", False, f"Error: {exc}")

# ── 6. merge_changes insert+update same key ─────────────────────────────
try:
    from hedron_data.collab import merge_changes
    from hedron_data.sources import DataChanges, CellUpdate

    local = DataChanges(inserts=({"id": "2", "v": "local"},))
    remote = DataChanges(updates=(CellUpdate(row_key="2", field="v", value="remote"),))
    result = merge_changes("v1", local, remote)
    confirmed = result.ok is True and result.accepted is not None
    if confirmed and result.accepted:
        confirmed = bool(result.accepted.inserts) and bool(result.accepted.updates)
    record(
        "merge_changes insert+update same key",
        confirmed,
        f"ok={result.ok} inserts={getattr(result.accepted, 'inserts', None)} "
        f"updates={getattr(result.accepted, 'updates', None)}",
    )
except Exception as exc:
    record("merge_changes insert+update same key", False, f"Error: {exc}")

# ── 7. rows_to_tree silent drop ──────────────────────────────────────────
try:
    from hedron_data.advanced import rows_to_tree, flatten_tree

    tree = rows_to_tree(
        [
            {"id": "0", "parent_id": 0},
            {"id": "1", "parent_id": None},
        ]
    )
    flat = flatten_tree(tree)
    confirmed = len(flat) == 1 and flat[0]["id"] == "1"
    record(
        "rows_to_tree silent drop unreachable node",
        confirmed,
        f"flat ids={[r['id'] for r in flat]}",
    )
except Exception as exc:
    record("rows_to_tree silent drop unreachable node", False, f"Error: {exc}")

# ── 8. normalize_rows column Secret leak ─────────────────────────────────
try:
    from hedron_core.security import Secret
    from hedron_data.normalize import normalize_rows

    rows = normalize_rows({"token": [Secret("leaked")]})
    confirmed = isinstance(rows[0]["token"], Secret)
    record(
        "normalize_rows column Secret leak",
        confirmed,
        f"token type={type(rows[0]['token']).__name__}",
    )
except Exception as exc:
    record("normalize_rows column Secret leak", False, f"Error: {exc}")

# ── 9. spreadsheet blank row phantom ─────────────────────────────────────
try:
    from hedron_data.spreadsheet import import_rows_xlsx, excel_col, _escape_xml_text

    sheet_rows = [["a", "b"], [], ["x", "y"]]
    row_xml = []
    for r_idx, values in enumerate(sheet_rows, start=1):
        cells = []
        for c_idx, value in enumerate(values):
            ref = f"{excel_col(c_idx)}{r_idx}"
            cells.append(
                f'<c r="{ref}" t="inlineStr"><is><t>{_escape_xml_text(value)}</t></is></c>'
            )
        row_xml.append(
            f'<row r="{r_idx}">{"".join(cells)}</row>' if cells else f'<row r="{r_idx}"/>'
        )
    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(row_xml)}</sheetData></worksheet>'
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            "</Types>",
        )
        zf.writestr(
            "xl/workbook.xml",
            '<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)
    rows = import_rows_xlsx(buf.getvalue())
    confirmed = rows == [{"a": "", "b": ""}, {"a": "x", "b": "y"}]
    record(
        "spreadsheet blank row phantom record",
        confirmed,
        f"rows={rows!r}",
    )
except Exception as exc:
    record("spreadsheet blank row phantom record", False, f"Error: {exc}")

# ── 10. pivot_rows count skips non-numeric ───────────────────────────────
try:
    from hedron_data.advanced import pivot_rows

    out = pivot_rows(
        [{"i": "a", "c": "x", "v": "label"}],
        index="i",
        columns="c",
        values="v",
        agg="count",
    )
    confirmed = out == []
    record(
        "pivot_rows count skips non-numeric values",
        confirmed,
        f"out={out!r}",
    )
except Exception as exc:
    record("pivot_rows count skips non-numeric values", False, f"Error: {exc}")

print("\n" + "=" * 70)
confirmed_count = sum(1 for _, c, _ in results if c)
print(f"SUMMARY: {confirmed_count}/{len(results)} confirmed")
for name, confirmed, detail in results:
    print(f"  {'✓' if confirmed else '✗'} {name}")
