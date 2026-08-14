# Human AT acceptance packet (0.21)

Protocol, privacy rules, task scripts, and the redacted ledger schema for phase **0.21**
(D-052).

| File | Role |
|---|---|
| [PROTOCOL.md](PROTOCOL.md) | Evaluation protocol (`PROTOCOL-021`) |
| [PRIVACY.md](PRIVACY.md) | Git vs private store / redaction |
| [task-scripts.md](task-scripts.md) | Reference-app task corpus |
| [ledger.schema.json](ledger.schema.json) | Redacted ledger row schema |
| [ledger/hat-example-0001.json](ledger/hat-example-0001.json) | Placeholder example row (not session evidence) |
| [037/PROTOCOL.md](037/PROTOCOL.md) | Scoped 0.37 form/primitive AT packet (not Supported) |
| [038/PROTOCOL.md](038/PROTOCOL.md) | Scoped 0.38 `hedron-chart` AT skeleton (not Supported; `A11Y-038`) |

Validate the packet:

```bash
uv run python scripts/check_human_at_packet.py
```

Gates: [release-gate-0.21.toml](../release-gate-0.21.toml) · checklist
[RELEASE_0_21.md](../RELEASE_0_21.md).
