---
status: shipped
---

# State APIs and boundaries

**Status:** Accepted

`SessionState` is a typed adapter over the host framework’s configured session mechanism. It is not a global Hedron store.

```python
from hedron import SessionState, session_state
from hedron_core import Model

class Preferences(Model):
    theme: str = "light"

@app.page("/prefs")
def preferences(state: SessionState[Preferences] = session_state("prefs", Preferences)):
    return PreferencesPanel(state.value)
```

Use `session_state(key, annotation)` as a FastAPI `Depends` factory. Bare `SessionState[T]` annotations alone are not enough for injection. Flask and Django adapters (later) preserve their framework-native session authority. Applications choose signing, storage, expiry, and authentication policy via the host middleware (`session_secret` on `Hedron()`).

## Ownership

- URL/path/query values: navigation and shareable filters.
- `FormModel` and actions: submitted request state.
- `SessionState[T]`: small session-scoped preferences and workflow data.
- Application services/databases: durable domain state.
- Cache APIs: derived values under explicit scope.
- Web Components: transient browser-local interaction.

Component instances are immutable render values and never durable actors. `SessionState` cannot hold arbitrary request objects, dependency instances, component trees, or unbounded data. Sensitive state follows the application’s session protection and must not appear in component identities, HTMX history snapshots, or Explorer examples.

## Authenticated caching flag

Set `request.state.hedron_authenticated = True` (typically from an auth dependency) so Hedron attaches `Cache-Control: private, no-store` when the security policy enables private authenticated caching.
