#!/usr/bin/env bash
# Publication reuses CI for the exact checked-out commit on a maintained branch.
set -euo pipefail

commit="$(git rev-parse HEAD)"
conclusion="$(gh run list --workflow ci.yml --commit "$commit" --event push \
  --json headBranch,conclusion --jq \
  '[.[] | select(.headBranch == "main" or .headBranch == "v1.0")][0].conclusion')"
if [[ "$conclusion" != success ]]; then
  echo "Release requires successful branch CI for $commit (got ${conclusion:-no run})." >&2
  echo "Complete CI on main or v1.0 before publishing this commit." >&2
  exit 1
fi
echo "ok: branch CI passed for $commit"
