# OpenAPI generator implementation

## Integration

Hedron contributes through FastAPI route metadata and a post-processing hook over the generated document. It does not build an independent HTTP schema.

For component routes, response content is `text/html` with a string schema and declared status codes and headers. Input schemas, dependencies, security requirements, parameters, and errors continue to come from FastAPI. JSON routes remain untouched.

## Extensions

Sanitized `x-hedron-*` objects reference stable registry identifiers, response modes, explicit addressability, props documentation, HTMX defaults, and optional development Explorer links. Production generation removes source locations, examples containing sensitive data, private preview URLs, and internal routes.

Operation IDs use a deterministic collision-checked generator shared with the registry. The schema is cached under the same invalidation rules as FastAPI and rebuilt after development registry replacement.

## Verification

Validate documents with an OpenAPI validator, snapshot mixed JSON/HTML applications, test security schemes and mounted routers, and assert the absence of secrets, absolute paths, dependency representations, and hidden internal resources.

