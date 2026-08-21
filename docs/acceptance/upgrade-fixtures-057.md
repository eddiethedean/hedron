# Upgrade fixtures for phase 0.57

**Published source:** `v0.56.0`  
**Refine baseline:** in-tree `0.56.1`  
**Target:** `v0.57.0`  
**Authority:** D-099 / D-100 / RFC-0084

## Compatibility expectations

- Existing layout `gap`, `Grid(columns=N)`, `FormGrid`, `Card`, `Section`, `Status`, `Table`,
  `FileUpload`, `ProcessFlow`, `FlowStep`, and AppShell slot calls remain valid.
- Existing control variants retain their default markup and appearance. Shared props are opt-in
  until a documented theme/container default is selected.
- Safe existing layout spacing gets an explicit CSP-safe mapping or an actionable migration
  diagnostic; unsupported values never silently compute to a fallback.
- AppShell slots continue accepting arbitrary `NodeLike` content alongside typed chrome helpers.
- The extras `AvatarProfile` recipe composes core Avatar/Identity or remains compatible.
- 0.55 upload budgets and 0.56 security/CSP authorities remain the enforcement source.

## Fixture themes

1. Golden 0.56 default markup and computed presentation.
2. Spacing values under standard/strict CSP, including invalid and compatibility cases.
3. Responsive Grid/FormGrid with long content, RTL, print, and 200% zoom.
4. Linked/action-bearing resource rows and table full-content paths.
5. Upload displayed-versus-enforced constraints and fragment replacement.
6. Status/process-flow reduced-motion and forced-colors equivalence.
7. AppShell arbitrary-slot compatibility beside typed chrome.
