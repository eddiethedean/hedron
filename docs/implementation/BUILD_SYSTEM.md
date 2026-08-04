# Build system implementation

## Commands and phases

`hedron build` loads configuration, discovers the application and explicit plugins, builds a
temporary registry, validates routes and models, compiles CSS, processes assets, generates OpenAPI
and documentation metadata, runs configured checks, and writes a versioned build manifest.
`hedron-jinja` checks templates through their configured Jinja loader rather than a core compiler.

All outputs are written to a temporary build directory and atomically promoted only after success. Failed builds leave the previous valid output intact. Inputs, tool versions, configuration, and artifact hashes are recorded for reproducibility.

## Development

`hedron dev` watches Python, CSS, Jinja template extensions, examples, and assets using
dependency graphs. It invalidates affected artifacts, builds a new registry snapshot, and reports
source-aware diagnostics. Reload never exposes a partially compiled application.

## Production

Production startup validates manifest compatibility and registered package versions. It does not
compile CSS or fetch remote assets by default. Build output is suitable for
wheels, containers, and external static hosting.

## Verification

Test clean/repeated builds, atomic failure, incremental invalidation, offline operation, deterministic outputs, compatibility rejection, source-map paths, package resources, and concurrent development rebuilds.
