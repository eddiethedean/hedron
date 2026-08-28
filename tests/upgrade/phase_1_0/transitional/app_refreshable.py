"""0.67 transitional fixture: app.refreshable -> app.view (manual review)."""


@app.refreshable("/status")
def status():
    return "ready"
