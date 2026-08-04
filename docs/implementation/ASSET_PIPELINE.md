# Asset pipeline implementation

## Inputs

Assets originate from Hedron core, component packages, scoped CSS, themes, browser modules, images,
chart adapters, Explorer, and application-registered roots. Metadata emitted by components invoked
through Jinja enters the same asset graph as metadata emitted by Python composition.

## Build

The pipeline resolves assets only from registered roots, calculates content fingerprints, rewrites component-relative references, deduplicates logical dependencies, and emits an immutable manifest. Production filenames include content hashes; development supports readable paths with no-cache behavior.

The initial strategy produces a global component CSS bundle plus explicit browser modules and media assets. Route-level splitting and HTMX asset negotiation are deferred. Static delivery uses Starlette `StaticFiles` or an external host configured from the same manifest.

## Security

Reject traversal, symlink escape, remote fetch by default, conflicting logical names, undeclared executable assets, disallowed MIME types, and unsafe inline requirements. Browser packages disclose scripts, workers, fonts, maps, and remote endpoints.

## Verification

Test deterministic manifests, MIME types, caching headers, mounted/root-path URLs, offline builds, CSS URL rewriting, duplicate content, package resources, symlink/traversal attacks, and missing asset diagnostics.
