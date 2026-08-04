#!/usr/bin/env bash
# Wrapper so local/CI docs builds stay free of Material's MkDocs 2.0 stderr banner.
set -euo pipefail
export NO_MKDOCS_2_WARNING="${NO_MKDOCS_2_WARNING:-1}"
exec mkdocs "$@"
