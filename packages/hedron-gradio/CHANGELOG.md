# Changelog

## [0.2.1] — 2026-08-24

### Changed
- Updated the Hedron core compatibility floor for the 0.61 interaction train.

## [0.43.0] — 2026-08-16

### Changed
- Coordinated train tip `0.43.0` (in-tree cut; tag/PyPI deferred).

### Fixed
- ``RemoteWorkflow`` fails closed when ``GradioClientAdapter.endpoints`` is empty
  or the named endpoint is not allowlisted (#338).

## [0.42.0] — 2026-08-14

### Added
- Phase 0.42 production-grade Web Component platform graduation (D-070).

### Changed
- Coordinated train tip `0.42.0` (in-tree cut; tag/PyPI deferred).

### Fixed
- Treat IPv4-mapped and IPv4-compatible IPv6 literals as their embedded IPv4 for private-host checks.
- ``validate_remote_url`` resolves A/AAAA and fails closed when any address is
  private/link-local unless ``allow_private_hosts`` is set (#268).
- ``ArtifactStore`` binds the same tenant/auth ``scope_key`` as jobs so
  download/delete fail closed across principals (#267).

## [0.2.0] — 2026-08-13

### Added
- `RemoteWorkflow` wraps GradioClientAdapter + GradioRemoteConfig/GradioEndpoint.


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
