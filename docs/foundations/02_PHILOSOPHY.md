# Philosophy

## Server-native components

React makes components the unit of composition. HTMX makes HTTP resources the unit of interaction. Hedron joins these ideas: a component may be a pure rendering primitive or, when explicitly declared addressable, an HTTP resource with an explicit contract.

## Familiarity without imitation

Hedron borrows component trees, props, children, slots, fragments, conditional rendering, and colocated ownership where they fit server rendering. It does not copy hooks, hydration, a virtual DOM, synthetic events, arbitrary client callbacks, or client-side state semantics.

## Productive before powerful

Beginners start with `Page`, `Card`, `Form`, `DataTable`, `DataEditor`, charts, and `Auto()`. They
should not need to understand the renderer, asset graph, or component registry. Advanced users can
progressively adopt explicit props, custom Python components, scoped styles, Web Components,
adapters, and compiler tooling that has independently justified its complexity. Hedron does not
assume a custom template language is inherently more progressive or approachable.

## Explain the magic

Hedron may infer mechanical facts such as response mode, a component URL, a safe HTMX target, a field editor, or an asset dependency. It may never infer trust, authorization, destructive intent, persistence rules, or business validation. Every inference must have a trace in the Component Explorer or CLI.

## Integrate rather than reinvent

Hedron owns web integration: lifecycle, rendering, transport, security defaults, accessibility contracts, asset delivery, discovery, and diagnostics. Libraries such as FastAPI, SQLAlchemy, Plotly, Altair, Matplotlib, Authlib, Pandas, and Polars retain their domain responsibilities.

## Performance with evidence

The first implementation is pure Python. Internal boundaries should permit targeted native acceleration, but Rust is introduced only when a representative benchmark identifies a bottleneck and parity can be tested against the Python implementation.
