---
status: shipped
---

# State APIs and boundaries


!!! note "Stability (0.11 train)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).

**Status:** Shipped · FastAPI flagship; adapters keep host-native sessions

`SessionState` is a typed adapter over the host framework’s configured session mechanism. It is not a global Hedron store.

## FastAPI usage

```python
from hedron import Hedron, Page, SessionState, Text, session_state
from hedron_core import Model

app = Hedron(title="Prefs", security="standard", session_secret="replace-me")


class Preferences(Model):
    theme: str = "light"


@app.page("/prefs")
def preferences(
    state: SessionState[Preferences] = session_state("prefs", Preferences),
) -> Page:
    return Page(Text(f"theme={state.value.theme}"), title="Prefs")
```

### `session_state(key, annotation)`

| Parameter | Type | Description |
|---|---|---|
| `key` | `str` | Session key under which the model is stored |
| `annotation` | `type[T]` | Pydantic/`Model` type to validate |

Returns a FastAPI `Depends` factory. Bare `SessionState[T]` annotations alone are **not**
enough for injection.

### `SessionState[T]`

| Member | Description |
|---|---|
| `value` | Current validated model instance |
| (mutations) | Assign through the adapter APIs used by the host session |

## Adapters

Flask and Django **Supported** adapters preserve framework-native session authority
(`flask.session`, Django sessions). They do not reimplement `session_state` injection;
read and write sessions with the host APIs and pass derived values into components.

Applications choose signing, storage, expiry, and authentication policy via the host
middleware (`session_secret` on `Hedron()` for FastAPI).

## Ownership

- URL/path/query values: navigation and shareable filters.
- `FormModel` and actions: submitted request state.
- `SessionState[T]`: small session-scoped preferences and workflow data.
- Application services/databases: durable domain state.
- Cache APIs: derived values under explicit scope.
- Web Components: transient browser-local interaction.

Component instances are immutable render values and never durable actors. `SessionState`
cannot hold arbitrary request objects, dependency instances, component trees, or unbounded
data. Sensitive state must not appear in component identities, HTMX history snapshots, or
Explorer examples.

## Authenticated caching flag

Set `request.state.hedron_authenticated = True` (typically from an auth dependency) so
Hedron attaches `Cache-Control: private, no-store` when the security policy enables private
authenticated caching.

## Errors

| Condition | Behavior |
|---|---|
| Invalid stored payload | Validation error from the model type |
| Missing `session_secret` in strict/production | Application refuses to start / rejects default |
| Using `SessionState` without `session_state(...)` | Dependency not injected; runtime/type errors |
