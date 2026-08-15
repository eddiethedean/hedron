# SBOM notes — phase 0.42

Wheel and npm artifacts for `hedron-elements` `0.42.x` and train-aligned fleet
packages must be reproducible from the repository lockfile (`uv.lock`) and the
`@hedron/elements` package.json mirror. Supported `.mjs` modules in the wheel
`static/` tree are byte-identical to `npm/modules/`. No React runtime is
packaged. Vulnerability triage for cut: no unresolved critical/high in
first-party Supported inventory dependencies.
