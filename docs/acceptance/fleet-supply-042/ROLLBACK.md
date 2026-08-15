# Rollback — phase 0.42

Pin `hedron>=0.41.0,<0.42` and `hedron-elements>=0.41.0,<0.42` to leave the
0.42 train. Disposable browser state (draft transfer, local UI) is never
migrated into server state. Mixed 0.42 modules with 0.41 servers fail closed
per element and preserve SSR/form/link/full-fragment navigation.
