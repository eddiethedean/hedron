# Contributing to Hedron specifications

## Before implementation

Identify the owning foundation and RFC. If behavior is absent or contradictory, update the specification before code. Public behavior additionally requires an API contract; a subsystem requires an implementation specification and acceptance coverage.

## RFC changes

Material proposals use the [RFC template](rfcs/TEMPLATE.md). Discuss alternatives and include security, accessibility, performance, testing, compatibility, migration, and open questions. Accepted behavior is changed through an explicit decision entry and RFC revision or superseding RFC.

## Implementation changes

An implementation change must state:

- owning RFC and decision identifiers;
- public API affected;
- implementation specification section;
- acceptance scenarios added or updated;
- compatibility and migration effect;
- new dependencies, assets, or plugin capabilities.

Do not expose private helpers merely to avoid designing a stable contract. Do not add a dependency to core when an optional adapter is sufficient. Do not introduce inferred authorization, persistence, or trust.

## Documentation definition of done

Examples compile, links resolve, names match public typing, errors and escape hatches are documented, and status/index tables are updated.
