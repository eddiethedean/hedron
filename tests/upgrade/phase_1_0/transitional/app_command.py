"""0.67 transitional fixture: app.command -> app.action (manual review)."""


@app.command("/ping")
def ping():
    return "pong"
