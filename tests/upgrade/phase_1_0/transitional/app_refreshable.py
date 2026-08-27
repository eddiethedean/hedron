"""0.67 transitional fixture: app.refreshable -> app.view (manual review)."""


@app.refreshable("/status")  # noqa: F821
def status():
    return "ready"
