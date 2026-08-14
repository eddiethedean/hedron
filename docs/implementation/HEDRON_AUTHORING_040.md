# Phase 0.40 implementation plan: authoring and interoperability

This plan turns [RFC-0060](../rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) / D-068 into reviewable
work. The living published tip is `v0.39.0`. Stage 0 (including this contract refine) adds
contracts only and does not change runtime behavior or versions. Tracking
[#95](https://github.com/eddiethedean/hedron/issues/95). Catalog:
[REACT_MIGRATION_MATRIX_040.md](REACT_MIGRATION_MATRIX_040.md). Interaction contracts:
[WEB_COMPONENT_INTERACTION_CONTRACTS.md](WEB_COMPONENT_INTERACTION_CONTRACTS.md).

## Outcome

Publish Hedron `v0.40.0` where third parties can author/package/test/inspect elements via public
contracts only, plugins/HDJ/Explorer/themes share element metadata, an optional `@hedron/elements`
modules/TS mirror may exist without requiring Node for Python consumers, and a React migration
matrix ships with an Experimental island bridge as docs/reference only.

Completion requires every row in
[`release-gate-0.40.toml`](../acceptance/release-gate-0.40.toml) Verified (React-island may remain
Experimental per D-068).

## Locked architecture

| Layer | Contract |
|---|---|
| Author kit | Public metadata/events/lifecycle/fallback/assets/a11y/diagnostics; `hedron new element` |
| Plugins | External consumer built without private APIs |
| HDJ / Explorer / theme | Shared element metadata; parts/slots/tokens |
| React matrix | Dispositions native/hedron/element/react-island/not-a-fit |
| Island bridge | Experimental docs/reference; not inside hedron-elements |
| Supply | Optional npm mirror content identity with wheels |

## Work breakdown

### Stage 0 — contract and evidence packet (complete)

- Accept D-068 / RFC-0060 Resolved questions (D-068).
- Add this plan, release packet, gate manifest, inventories, upgrade fixtures, review brief,
  [REACT_MIGRATION_MATRIX_040.md](REACT_MIGRATION_MATRIX_040.md), and scoped [AT-040](../acceptance/human-at/040/PROTOCOL.md).
- Bind tracking [#95](https://github.com/eddiethedean/hedron/issues/95) and remediations
  #162/#203/#204/#219/#220/#222.
- Rebaseline living published tip acknowledgment to `v0.39.0`.
- Add lenient packet verification to CI.
- Do not modify authoring runtime, package versions, living pins, or release status.

**Explicitly forbidden until Stage 1+:** scaffold implementation, React bridge code, HDJ/Explorer
theme runtime, npm publish, workspace or tip bump, flipping any 0.40 gate to Verified,
adopter-facing “0.40 Published” claims.

Exit: `python scripts/verify_pkg_40.py --allow-planned`.

### Stage 1+ (sketched only)

- AUTHOR-040 / PLUGIN-040: author kit + external consumer.
- HDJ-040 / THEME-040 / EXPLORER-040 / CONF-040: metadata parity and fixtures.
- MIGRATE-040: matrix + Experimental island reference.
- SUPPLY-040 / REGRESS-040 / PKG-040: supply, 6-issue packet, cut `v0.40.0`.

## Cut commands

During planning and implementation:

```bash
python scripts/verify_pkg_40.py --allow-planned
```

At cut:

```bash
python scripts/verify_pkg_40.py
python scripts/check_release_gate.py 0.40.0 --execute-verified
```
