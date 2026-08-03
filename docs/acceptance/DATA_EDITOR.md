# DataEditor acceptance

## Data and editing

- [x] Lists, Hedron models, Pandas, Polars, and PyArrow inputs work when their extras are installed.
- [x] Text, number, decimal, boolean, date, datetime, enum/select, hidden, and read-only columns derive from models and allow explicit override.
- [x] Manual batch save, insertion, deletion, validation retention, and stable row keys work.
- [x] Typed changes transmit deltas rather than the entire dataset.
- [x] Optimistic concurrency returns actionable cell/row conflicts.
- [x] Large sources use bounded server-side paging, sorting, and allowlisted filtering.

## Security and usability

- [x] CSRF and explicit authorization protect every mutation.
- [x] Forged changes cannot edit read-only, hidden, or unauthorized fields.
- [x] Pending edits survive validation errors and focus the first invalid cell.
- [x] Keyboard navigation, screen-reader labeling, status announcements, and CSV download work.
- [x] Explorer uses isolated data by default and shows schema, policy, changes, conflicts, timing, and endpoints.

## Exit

The reference CRUD application edits a paged authenticated dataset safely with no backend-specific API leaking into application components.
