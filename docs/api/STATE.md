# State APIs and boundaries

**Status:** Accepted

`SessionState` is a typed adapter over the host framework’s configured session mechanism. It is not a global Hedron store.

```python
def preferences(state: SessionState[Preferences]) -> PreferencesPanel:
    return PreferencesPanel(state.value)
```

The FastAPI adapter obtains session state through dependency injection. Flask and Django adapters preserve their framework-native session authority. Applications choose signing, storage, expiry, and authentication policy.

## Ownership

- URL/path/query values: navigation and shareable filters.
- `FormModel` and actions: submitted request state.
- `SessionState[T]`: small session-scoped preferences and workflow data.
- Application services/databases: durable domain state.
- Cache APIs: derived values under explicit scope.
- Web Components: transient browser-local interaction.

Component instances are immutable render values and never durable actors. `SessionState` cannot hold arbitrary request objects, dependency instances, component trees, or unbounded data. Sensitive state follows the application’s session protection and must not appear in component identities, HTMX history snapshots, or Explorer examples.

