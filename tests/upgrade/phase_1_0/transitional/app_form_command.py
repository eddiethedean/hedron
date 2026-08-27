"""0.67 transitional fixture: app.form_command -> app.action (manual review)."""


@app.form_command("/notes")  # noqa: F821
def add_note(message: str):
    return message
