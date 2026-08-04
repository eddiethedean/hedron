# RFC-0003: Component model

**Status:** Accepted

## Model

A component has an identity, props contract, children or named slots, render implementation, optional examples, assets, styles, documentation, and browser behavior. Its `render()` method returns `NodeLike`; only the top-level rendering engine creates a validated `RenderResult`.

Components are either:

- **renderable**, with no HTTP resource; or
- **addressable**, created by an explicitly registered factory with an HTTP input contract and security context.

## Composition

The model supports native elements, text, fragments, components, optional values, sequences, children, and named slots. Standard HTML names remain canonical; Python aliases such as `class_` are authoring conveniences only.

Props are immutable during rendering. Stable component identities may support targets and diagnostics but must exclude secrets and must never authorize requests.

## Errors

Unknown props, invalid children, missing slots, unsafe attributes, and return-contract mismatches fail at definition, compilation, startup, or render time with component and source context. Silent coercion is avoided when it can hide a mistake.

## Acceptance criteria

- The legacy HDN parity sample lowers to equivalent node semantics; D-040/RFC-0031 revoke any
  broader language commitment until declarative authoring is selected or removed.
- Nested components render with deterministic escaping and attribute normalization.
- A renderable component cannot be requested until separately declared addressable.
- Examples and tests can construct components without a live server.
