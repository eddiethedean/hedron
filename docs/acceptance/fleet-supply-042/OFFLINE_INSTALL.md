# Offline install — phase 0.42

Install from wheels/sdists and the optional `@hedron/elements` tarball without
CDN script tags. Python apps must not require a bundler or Node toolchain.
CDN refusal: applications that cannot reach external CDNs continue to serve
Supported elements from package resources. Removing `hedron-elements` leaves
ordinary form/link/full-fragment SSR paths intact for non-element surfaces.
