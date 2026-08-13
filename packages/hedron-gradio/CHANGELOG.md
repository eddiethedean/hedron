## [0.2.0] — 2026-08-13

### Added

- Production-grade remote policy: `GradioRemoteConfig`, destination allowlist, SSRF/private-host
  defenses, and diagnostic redaction (RFC-0067 / phase 0.34).
- Bounded `ArtifactStore` with extension allowlist, capacity limits, and TTL eviction.
- Scoped `GradioJobManager` with deadlines, cancel, and tenant/subject isolation.
- Hugging Face Space helpers: `hf_space_base_url`, `hf_remote_config_for_space`,
  `translate_hf_vendor_status`, recorded fixtures.

### Changed

- Package maturity graduates to **Beta** (`>=0.2.0,<0.3`); Alpha `0.1.x` remains upgrade source.
- `GradioClientAdapter` validates `base_url` against `remote_config` on enabled paths.
- Job status uses scoped manager semantics instead of instant in-memory completion.

## [0.1.0] — 2026-08-06

### Added

- Initial Alpha release of `GradioClientAdapter` (RFC-0049): disabled by default,
  optional `gradio_client` discovery, predict/job/stream contracts, in-memory
  file transport, version compatibility checks, and Hugging Face vendor nodes.
- Migration inventory diagnostics (`GRADIO_NON_PARITY`) and optional
  `hedron.plugins` FeatureManifest registration.
