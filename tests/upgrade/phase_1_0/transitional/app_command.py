"""0.67 transitional fixture: app.command -> app.action (manual review)."""


@app.command("/ping")  # noqa: F821
def ping():
    return "pong"
