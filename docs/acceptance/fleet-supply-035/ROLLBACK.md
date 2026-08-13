# Fleet rollback notes (SUPPLY-035)

Owning gate: `SUPPLY-035`.

## Rollback policy

- pin the previous published train: `hedron>=0.34.0,<0.35`
- Independent satellites keep their own ceilings (`hedron-mcp` / `hedron-gradio` `>=0.2.0,<0.3`,
  `fastapi-workbench>=1,<2`)
- Restore application lockfiles / image digests from the prior release tag `v0.34.0`

## Pass criteria

- Previous train remains installable from PyPI after `v0.35.0` publishes
- Inventory `evidence` pointers for graduated packages remain valid on historical tags
- No forced upgrade of Experimental live transports is implied by the 0.35 cut
