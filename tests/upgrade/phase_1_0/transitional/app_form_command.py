"""0.67 transitional fixture: app.form_command -> app.action (manual review)."""


@app.form_command("/notes")
def add_note(message: str):
    return message
