# Human AT protocol — phase 0.37 (scoped)

Representative screen-reader sessions for form-associated reference elements (`hedron-field-text`, `hedron-field-choice`, `hedron-field-file`) and primitives (`hedron-disclosure`, `hedron-dialog`).

This packet is **scoped AT evidence** for `AT-037` only. It does not claim Supported human AT (see #86 / D-052).

## Sessions

1. Complete a native-fallback form with field-text and field-choice before JS upgrade.
2. Toggle disclosure and open dialog with keyboard-only navigation after upgrade.
3. Submit async action and confirm busy/status announcement restraint.

Record outcomes in `ledger/` using the redacted schema from `../ledger.schema.json`.
