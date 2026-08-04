# Build system implementation

## Commands and phases

`hedron build` loads configuration, discovers the application and explicit plugins, builds a
temporary registry, validates routes and models, compiles CSS and any existing experimental HDN
compatibility sources, processes assets, generates OpenAPI and documentation metadata, runs
configured checks, and writes a versioned build manifest. D-040/RFC-0031 replace the
HDN step; it is not a forward build-contract dependency.

All outputs are written to a temporary build directory and atomically promoted only after success. Failed builds leave the previous valid output intact. Inputs, tool versions, configuration, and artifact hashes are recorded for reproducibility.

## Development

`hedron dev` watches Python, CSS, examples, assets, and existing experimental HDN sources using
dependency graphs. It invalidates affected artifacts, builds a new registry snapshot, and reports
source-aware diagnostics. Reload never exposes a partially compiled application.

## Production

Production startup validates manifest compatibility and registered package versions. It does not
compile CSS or legacy HDN sources or fetch remote assets by default. Build output is suitable for
wheels, containers, and external static hosting.

## Verification

Test clean/repeated builds, atomic failure, incremental invalidation, offline operation, deterministic outputs, compatibility rejection, source-map paths, package resources, and concurrent development rebuilds.
