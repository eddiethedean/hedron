#!/usr/bin/env python3
"""Re-verify UploadFlow authorize and multi-file with isolated app names."""

from fastapi import Depends
from fastapi.testclient import TestClient
from hedron import Hedron, Text, UploadFlow
from hedron.upload import UploadField, UploadBudget

# --- authorize on result vs upload ---
app = Hedron(title="auth-test", security="development", explorer="off", session_secret="a" * 32)

def require_auth():
    return "ok"

app.include_feature(
    UploadFlow(
        name="uploads",
        field=UploadField(name="file"),
        authorize=Depends(require_auth),
        store=lambda h: "stored",
        result=lambda s: Text(f"R:{s}"),
    )
)

for route in app.routes:
    path = getattr(route, "path", "")
    if path in ("/uploads/upload", "/uploads/result"):
        deps = [getattr(d, "call", d) for d in route.dependant.dependencies]
        print(f"{path}: {len(route.dependant.dependencies)} deps -> {[getattr(x, '__name__', str(x)) for x in deps]}")

# --- multi-file last wins ---
calls: list[str] = []
app2 = Hedron(title="multi", security="development", explorer="off", session_secret="b" * 32)
app2.include_feature(
    UploadFlow(
        name="batch",
        field=UploadField(name="file", budget=UploadBudget(maximum_size=10000, maximum_count=3)),
        authorize=Depends(lambda: None),
        store=lambda h: calls.append(h.filename) or h.filename,
        result=lambda s: Text(f"stored={s}"),
    )
)
c = TestClient(app2)
csrf = c.get("/batch/upload").cookies.get("hedron_csrf")
r = c.post(
    "/batch/upload",
    data={"csrf_token": csrf},
    files=[
        ("file", ("a.txt", b"a", "text/plain")),
        ("file", ("b.txt", b"b", "text/plain")),
    ],
)
print(f"multi-file calls={calls} response={r.text!r} status={r.status_code}")
