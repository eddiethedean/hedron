# DataEditor acceptance

## Data and editing

- [ ] Lists, Hedron models, Pandas, Polars, and PyArrow inputs work when their extras are installed.
- [ ] Text, number, decimal, boolean, date, datetime, enum/select, hidden, and read-only columns derive from models and allow explicit override.
- [ ] Manual batch save, insertion, deletion, validation retention, and stable row keys work.
- [ ] Typed changes transmit deltas rather than the entire dataset.
- [ ] Optimistic concurrency returns actionable cell/row conflicts.
- [ ] Large sources use bounded server-side paging, sorting, and allowlisted filtering.

## Security and usability

- [ ] CSRF and explicit authorization protect every mutation.
- [ ] Forged changes cannot edit read-only, hidden, or unauthorized fields.
- [ ] Pending edits survive validation errors and focus the first invalid cell.
- [ ] Keyboard navigation, screen-reader labeling, status announcements, and CSV download work.
- [ ] Explorer uses isolated data by default and shows schema, policy, changes, conflicts, timing, and endpoints.

## Exit

The reference CRUD application edits a paged authenticated dataset safely with no backend-specific API leaking into application components.

