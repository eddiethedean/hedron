# Model system implementation

## Responsibilities

The model package implements Hedron-owned `Model`, `Props`, `FormModel`, `EventPayload`, `Field`, `Secret`, `TrustedHtml`, and safe URL types on a constrained Pydantic foundation.

At class creation it inspects annotations and Hedron metadata, rejects unsupported constructs, freezes a portable field schema, and emits registry-ready documentation and presentation metadata. Pydantic schemas are implementation inputs, not the canonical public representation.

## Internal artifacts

- `ModelSchema` with stable field identifiers, types, defaults, constraints, and metadata.
- Redaction policy for secret-bearing paths.
- Conversion rules for HTTP inputs, component props, form controls, data columns, examples, and Explorer views.
- Stable diagnostic codes for unsupported types and contradictory metadata.

## Guardrails

Props and endpoint inputs remain separate schemas. Extra fields are forbidden by default. Custom validators are permitted only through a documented inspectable extension contract. Representations, validation errors, examples, identity generation, and cache keys use the redaction policy.

## Verification

Test supported and rejected types, nested redaction, schema determinism, Pydantic version compatibility, form metadata, extra-field handling, and absence of Pydantic-specific objects from public serialization.

