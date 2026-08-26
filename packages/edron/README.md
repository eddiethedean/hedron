# Edron

Edron is a class-oriented Python authoring facade over Hedron. It keeps Hedron as the renderer,
router, interaction, state, styling, and security authority.

```python
import edron as ed

app = ed.App(title="Hello")


@app.page("/", title="Hello")
class Home(ed.Page):
    def render(self) -> None:
        self.heading("Hello, Edron")
        self.text("A small Python vocabulary over native Hedron.")
```

Edron 0.3 is a Beta implementation line. Native Hedron objects remain available through
`app.hedron` and `Page.include()`. Use `edron check` for non-executing editor feedback,
`edron explain` for source-mapped registration facts, and `edron new` for teaching scaffolds.

Data workspaces are explicit and application-owned:

```python
columns = (ed.Column("id", read_only=True), ed.Column("name", writable=True))
source = ed.DataSource.in_memory(
    [{"id": "1", "name": "Ada"}],
    columns=columns,
    writable_fields=("name",),
)
workspace = ed.DataWorkspace("people", source=source, columns=columns)
```

Add an `EditPolicy` with explicit authorization to make a workspace editable. Edron never owns
database sessions, transactions, authorization state, persistence, or audit storage.
