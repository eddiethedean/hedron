# Identifier and fingerprint contract

**Status:** Accepted for the phase 0.0 baseline

Identifiers are deterministic, inspectable, collision checked, and never security credentials.

## Logical identifiers

- Component type: `<distribution>:<module>.<qualified-name>`, for example `acme-widgets:acme_widgets.users.UserTable`.
- Registry resource: `<kind>:<logical-id>`, where kind is `component`, `page`, `action`, `theme`, `plugin`, or `asset`.
- FastAPI operation ID: a readable category and normalized route name such as `component_user_table`.

Applications may provide an explicit public name. Duplicate logical or operation identifiers fail at registry sealing.

## DOM instance identifiers

Generated DOM IDs use `h-` plus the first 20 lowercase base32 characters of SHA-256 over a versioned canonical identity record. That record may contain the logical component ID, route identity, explicit `key`, and fields declared `identity=True`. It never contains a `Secret`, dependency object, raw request object, or undeclared props.

Collisions within one render are detected and fail with a diagnostic. Explicit developer IDs are validated but preserved. IDs are stable only within the documented identity inputs and format version; they are not authorization, anti-CSRF, signing, or cache-secrecy mechanisms.

## Assets and compiled artifacts

Asset manifests store the full SHA-256 content digest. Filenames use the first 20 lowercase hexadecimal characters, for example `components.a1b2c3d4e5f60718293a.css`. A prefix collision lengthens the filename rather than overwriting an artifact.

Jinja template inventories, CSS symbol manifests, registry snapshots, and build manifests include a format version and full content digest. Absolute paths, timestamps, and import order do not participate in reproducible content identity.

## Scoped CSS

CSS scope input is the logical component identifier plus the scoped symbol and compiler format version. Development names remain readable; production names may be shorter but map through the emitted manifest.
