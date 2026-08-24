#!/usr/bin/env python3
"""Verify additional bug candidates."""

import asyncio

print("=== 1. prepare_tree skips _NativeElement children ===")
from hedron_core.html import html
from hedron_core.component import Component
from hedron_core.models import Props
from hedron_core.prepare import prepare_tree, PrepareContext


class P(Props):
    pass


class Panel(Component[P]):
    props_type = P

    def __init__(self):
        super().__init__(P())
        self.ok = False

    async def prepare(self, ctx: PrepareContext) -> None:
        self.ok = True

    def render(self):
        return html.span("x")


async def test_prepare():
    p = Panel()
    await prepare_tree(html.div(p))
    print(f"Panel.ok after html.div wrapper: {p.ok}")
    p2 = Panel()
    await prepare_tree(p2)
    print(f"Panel.ok direct: {p2.ok}")


asyncio.run(test_prepare())

print("\n=== 2. SafeUrl rejects foo..bar ===")
from hedron_core.security import SafeUrl, UrlPurpose

try:
    SafeUrl.parse("/assets/foo..bar.png", purpose=UrlPurpose.ASSET)
    print("Accepted foo..bar (no bug)")
except Exception as exc:
    print(f"Rejected: {type(exc).__name__}: {exc}")

print("\n=== 3. UploadFlow multi-file (isolated process) ===")
from fastapi import Depends
from fastapi.testclient import TestClient
from hedron import Hedron, Text, UploadFlow
from hedron.upload import UploadField, UploadBudget

calls: list[str] = []
app = Hedron(title="multi", security="development", explorer="off", session_secret="b" * 32)
app.include_feature(
    UploadFlow(
        name="batch",
        field=UploadField(name="file", budget=UploadBudget(maximum_size=10000, maximum_count=3)),
        authorize=Depends(lambda: None),
        store=lambda h: calls.append(h.filename) or h.filename,
        result=lambda s: Text(f"stored={s}"),
    )
)
c = TestClient(app)
csrf = c.get("/batch/upload").cookies.get("hedron_csrf")
r = c.post(
    "/batch/upload",
    data={"csrf_token": csrf},
    files=[
        ("file", ("a.txt", b"a", "text/plain")),
        ("file", ("b.txt", b"b", "text/plain")),
    ],
)
print(f"calls={calls} status={r.status_code} body={r.text!r}")

print("\n=== 4. UploadFlow duplicate route names across flows ===")
try:
    app2 = Hedron(title="x", security="development", explorer="off", session_secret="c" * 32)
    app2.include_feature(
        UploadFlow(
            name="a",
            field=UploadField(),
            authorize=Depends(lambda: None),
            store=lambda h: "x",
            result=lambda s: Text("x"),
        )
    )
    app2.include_feature(
        UploadFlow(
            name="b",
            field=UploadField(),
            authorize=Depends(lambda: None),
            store=lambda h: "y",
            result=lambda s: Text("y"),
        )
    )
    print("Two UploadFlows registered OK (no bug)")
except Exception as exc:
    print(f"Second UploadFlow failed: {type(exc).__name__}: {exc}")
