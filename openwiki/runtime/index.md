# Files

- [Application and Runtime Lifecycle](application-lifecycle.md) - Application-owned runtime context, ASGI request binding, lifespan startup, registry sealing, and production build gates.
- [Runtime state and background jobs](jobs-and-state.md) - Hedron binds application-owned runtime services to each request and composes scoped, authorized background-job submission, polling, cancellation, and result views around a JobBackend.
