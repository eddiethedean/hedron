# Rendering engine implementation

## Pipeline

1. Accept a component and render context.
2. Validate the declared component contract.
3. Resolve optional prepared state before rendering.
4. Build a normalized node tree.
5. Collect registry-declared assets and metadata.
6. Serialize through the HTML serializer.
7. Produce a `RenderResult` containing HTML bytes/string, mode, assets, headers, identity map, and trace.

## Node model

The private node algebra contains text, native element, fragment, component boundary, trusted HTML, comment where needed, and empty nodes. Construction normalizes optional and sequence values without flattening unsafe arbitrary iterables. Native elements use canonical HTML tag and attribute metadata.

Rendering is synchronous, reentrant, and request-local. It performs no network or database I/O. Cycle detection reports the component path. Depth and output limits are configurable defense-in-depth controls.

## Page and fragment modes

A page render composes document shell, metadata, body, and asset references. A fragment render emits only the selected component content plus approved HTMX headers or out-of-band nodes. Mode selection occurs before serialization and is recorded in the trace.

## Verification

Golden tests cover composition, slots, pages, fragments, identity, assets, trace boundaries, cycles, limits, and sync determinism. Benchmarks separate tree construction from serialization.

