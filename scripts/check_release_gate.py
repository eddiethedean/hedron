#!/usr/bin/env python3
"""Fail if a release tag is not ready for public publication."""

from __future__ import annotations

import argparse
import hashlib
import math
import re
import shlex
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import cast

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_BY_MAJOR_MINOR = {
    "0.6": ROOT / "docs" / "acceptance" / "release-gate-0.6.toml",
    "0.7": ROOT / "docs" / "acceptance" / "release-gate-0.7.toml",
    "0.8": ROOT / "docs" / "acceptance" / "release-gate-0.8.toml",
    "0.9": ROOT / "docs" / "acceptance" / "release-gate-0.9.toml",
    "0.10": ROOT / "docs" / "acceptance" / "release-gate-0.10.toml",
    "0.11": ROOT / "docs" / "acceptance" / "release-gate-0.11.toml",
    "0.12": ROOT / "docs" / "acceptance" / "release-gate-0.12.toml",
    "0.13": ROOT / "docs" / "acceptance" / "release-gate-0.13.toml",
    "0.14": ROOT / "docs" / "acceptance" / "release-gate-0.14.toml",
    "0.15": ROOT / "docs" / "acceptance" / "release-gate-0.15.toml",
    "0.16": ROOT / "docs" / "acceptance" / "release-gate-0.16.toml",
    "0.17": ROOT / "docs" / "acceptance" / "release-gate-0.17.toml",
    "0.18": ROOT / "docs" / "acceptance" / "release-gate-0.18.toml",
    "0.19": ROOT / "docs" / "acceptance" / "release-gate-0.19.toml",
    "0.20": ROOT / "docs" / "acceptance" / "release-gate-0.20.toml",
    "0.21": ROOT / "docs" / "acceptance" / "release-gate-0.21.toml",
    "0.22": ROOT / "docs" / "acceptance" / "release-gate-0.22.toml",
    "0.23": ROOT / "docs" / "acceptance" / "release-gate-0.23.toml",
    "0.24": ROOT / "docs" / "acceptance" / "release-gate-0.24.toml",
    "0.25": ROOT / "docs" / "acceptance" / "release-gate-0.25.toml",
    "0.26": ROOT / "docs" / "acceptance" / "release-gate-0.26.toml",
    "0.27": ROOT / "docs" / "acceptance" / "release-gate-0.27.toml",
    "0.28": ROOT / "docs" / "acceptance" / "release-gate-0.28.toml",
    "0.29": ROOT / "docs" / "acceptance" / "release-gate-0.29.toml",
    "0.30": ROOT / "docs" / "acceptance" / "release-gate-0.30.toml",
    "0.31": ROOT / "docs" / "acceptance" / "release-gate-0.31.toml",
    "0.32": ROOT / "docs" / "acceptance" / "release-gate-0.32.toml",
    "0.33": ROOT / "docs" / "acceptance" / "release-gate-0.33.toml",
    "0.34": ROOT / "docs" / "acceptance" / "release-gate-0.34.toml",
    "0.35": ROOT / "docs" / "acceptance" / "release-gate-0.35.toml",
    "0.36": ROOT / "docs" / "acceptance" / "release-gate-0.36.toml",
    "0.37": ROOT / "docs" / "acceptance" / "release-gate-0.37.toml",
    "0.38": ROOT / "docs" / "acceptance" / "release-gate-0.38.toml",
    "0.39": ROOT / "docs" / "acceptance" / "release-gate-0.39.toml",
    "0.40": ROOT / "docs" / "acceptance" / "release-gate-0.40.toml",
    "0.42": ROOT / "docs" / "acceptance" / "release-gate-0.42.toml",
    "0.43": ROOT / "docs" / "acceptance" / "release-gate-0.43.toml",
    "0.44": ROOT / "docs" / "acceptance" / "release-gate-0.44.toml",
    "0.45": ROOT / "docs" / "acceptance" / "release-gate-0.45.toml",
    "0.47": ROOT / "docs" / "acceptance" / "release-gate-0.47.toml",
    "0.48": ROOT / "docs" / "acceptance" / "release-gate-0.48.toml",
    "0.49": ROOT / "docs" / "acceptance" / "release-gate-0.49.toml",
    "0.50": ROOT / "docs" / "acceptance" / "release-gate-0.50.toml",
    "0.51": ROOT / "docs" / "acceptance" / "release-gate-0.51.toml",
    "0.52": ROOT / "docs" / "acceptance" / "release-gate-0.52.toml",
    "0.53": ROOT / "docs" / "acceptance" / "release-gate-0.53.toml",
    "0.54": ROOT / "docs" / "acceptance" / "release-gate-0.54.toml",
    "0.55": ROOT / "docs" / "acceptance" / "release-gate-0.55.toml",
    "0.56": ROOT / "docs" / "acceptance" / "release-gate-0.56.toml",
    "0.57": ROOT / "docs" / "acceptance" / "release-gate-0.57.toml",
    "0.58": ROOT / "docs" / "acceptance" / "release-gate-0.58.toml",
    "0.59": ROOT / "docs" / "acceptance" / "release-gate-0.59.toml",
    "0.60": ROOT / "docs" / "acceptance" / "release-gate-0.60.toml",
    "0.61": ROOT / "docs" / "acceptance" / "release-gate-0.61.toml",
    "0.62": ROOT / "docs" / "acceptance" / "release-gate-0.62.toml",
    "0.63": ROOT / "docs" / "acceptance" / "release-gate-0.63.toml",
    "0.64": ROOT / "docs" / "acceptance" / "release-gate-0.64.toml",
    "0.65": ROOT / "docs" / "acceptance" / "release-gate-0.65.toml",
    "0.66": ROOT / "docs" / "acceptance" / "release-gate-0.66.toml",
    "0.67": ROOT / "docs" / "acceptance" / "release-gate-0.67.toml",
    "1.0": ROOT / "docs" / "acceptance" / "release-gate-1.0.toml",
    "1.1": ROOT / "docs" / "acceptance" / "release-gate-1.1.toml",
    "1.2": ROOT / "docs" / "acceptance" / "release-gate-1.2.toml",
    "1.3": ROOT / "docs" / "acceptance" / "release-gate-1.3.toml",
}
DEFAULT_EVIDENCE = EVIDENCE_BY_MAJOR_MINOR["0.6"]
PHASE_120_EVIDENCE_IDS = (
    "POLICY-120",
    "FREEZE-120",
    "METADATA-120",
    "CHECKS-120",
    "TYPING-120",
    "STDLIB-120",
    "COMPAT-120",
    "RUNTIME-120",
    "NATIVE-120",
    "PKG-120",
    "DOCS-120",
    "RELEASE-120",
)
PHASE_130_EVIDENCE_IDS = (
    "FREEZE-130",
    "CONTRACT-130",
    "HOST-130",
    "LOCATOR-130",
    "SETTLE-130",
    "ERROR-130",
    "ARTIFACT-130",
    "PYTEST-130",
    "SATELLITE-130",
    "BEHAVIOR-130",
    "A11Y-130",
    "SECURITY-130",
    "PERF-130",
    "COMPAT-130",
    "DOCS-130",
    "PKG-130",
    "RELEASE-130",
)
PHASE_130_EVIDENCE_ONLY_PATHS = frozenset(
    {
        "docs/acceptance/RELEASE_1_3.md",
        "docs/acceptance/release-gate-1.3.toml",
    }
)
PHASE_130_EVIDENCE_ONLY_PREFIX = "docs/acceptance/evidence-130/"
PHASE_130_BUDGET_IDS = (
    "host",
    "browser",
    "settle",
    "structured_artifacts",
    "synthetic_capture",
    "parallel",
    "compatibility",
)
# Includes historical ``release`` attestation used by older gate manifests.
KNOWN_CI_JOBS = frozenset(
    {"test", "quality", "browser", "evidence", "realwb", "realconnect", "packaging", "release"}
)
# Commands that must not be re-entered from --execute-verified.
_RECURSIVE_SCRIPT_NAMES = frozenset(
    {
        "check_release_gate.py",
        "verify_pkg_09.py",
        "verify_pkg_10.py",
        "verify_pkg_11.py",
        "verify_pkg_12.py",
        "verify_pkg_13.py",
        "verify_pkg_14.py",
        "verify_pkg_15.py",
        "verify_pkg_16.py",
        "verify_pkg_17.py",
        "verify_pkg_18.py",
        "verify_pkg_19.py",
        "verify_pkg_20.py",
        "verify_pkg_21.py",
        "verify_pkg_22.py",
        "verify_pkg_23.py",
        "verify_pkg_24.py",
        "verify_pkg_25.py",
        "verify_pkg_26.py",
        "verify_pkg_27.py",
        "verify_pkg_28.py",
        "verify_pkg_29.py",
        "verify_pkg_30.py",
        "verify_pkg_31.py",
        "verify_pkg_32.py",
        "verify_pkg_33.py",
        "verify_pkg_34.py",
        "verify_pkg_35.py",
        "verify_pkg_36.py",
        "verify_pkg_37.py",
        "verify_pkg_38.py",
        "verify_pkg_43.py",
        "verify_pkg_44.py",
        "verify_pkg_45.py",
        "verify_pkg_46.py",
        "verify_pkg_47.py",
        "verify_pkg_48.py",
        "verify_pkg_49.py",
        "verify_pkg_50.py",
        "verify_pkg_51.py",
        "verify_pkg_56.py",
        "verify_pkg_57.py",
        "verify_pkg_58.py",
        "verify_pkg_60.py",
        "verify_pkg_61.py",
        "ci_checks.sh",
    }
)


def evidence_manifest_for(version: str) -> Path:
    parts = version.split(".")
    if len(parts) >= 2:
        key = f"{parts[0]}.{parts[1]}"
        if key in EVIDENCE_BY_MAJOR_MINOR:
            return EVIDENCE_BY_MAJOR_MINOR[key]
        if parts[0] == "1":
            raise ValueError(f"no explicit release evidence manifest for version {version!r}")
    return DEFAULT_EVIDENCE


def _bound_record_errors(
    base_dir: Path,
    record_value: object,
    digest_value: object,
    label: str,
) -> list[str]:
    errors: list[str] = []
    record = str(record_value).strip() if isinstance(record_value, str) else ""
    digest = str(digest_value).strip() if isinstance(digest_value, str) else ""
    if not record:
        return [f"{label}: retained evidence path is required"]
    relative = PurePosixPath(record)
    if (
        relative.is_absolute()
        or relative.as_posix() != record
        or "\\" in record
        or any(part in {".", ".."} for part in relative.parts)
    ):
        return [f"{label}: evidence path must be a normalized repository-relative path"]
    candidate = base_dir
    for part in relative.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            return [f"{label}: evidence path must not traverse symlinks"]
    try:
        resolved = candidate.resolve(strict=True)
    except OSError:
        return [f"{label}: retained evidence file does not exist: {record}"]
    try:
        _ = resolved.relative_to(base_dir.resolve())
    except ValueError:
        return [f"{label}: evidence file must remain inside {base_dir}"]
    if not resolved.is_file():
        return [f"{label}: retained evidence path is not a file: {record}"]
    try:
        _ = base_dir.resolve().relative_to(ROOT.resolve())
    except ValueError:
        pass
    else:
        try:
            repository_path = resolved.relative_to(ROOT.resolve()).as_posix()
            _ = subprocess.check_output(
                ["git", "ls-files", "--error-unmatch", "--", repository_path],
                cwd=ROOT,
                text=True,
                stderr=subprocess.DEVNULL,
            )
        except (OSError, subprocess.CalledProcessError, ValueError):
            return [f"{label}: evidence file must be committed in the release source"]
    if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        return [f"{label}: evidence_sha256 must be a lowercase SHA-256 digest"]
    sha256 = hashlib.sha256()
    try:
        with resolved.open("rb") as evidence_file:
            for chunk in iter(lambda: evidence_file.read(1024 * 1024), b""):
                sha256.update(chunk)
    except OSError as exc:
        return [f"{label}: unable to read retained evidence: {exc}"]
    if sha256.hexdigest() != digest:
        errors.append(f"{label}: retained evidence SHA-256 does not match")
    return errors


def _validate_phase_130_release_records(
    data: dict[str, object],
    rows: list[object],
    path: Path,
) -> list[str]:
    errors: list[str] = []
    evidence_root = path.parent
    source_revisions: set[str] = set()
    for row_value in rows:
        if not isinstance(row_value, dict):
            continue
        row = cast(Mapping[str, object], row_value)
        if str(row.get("state", "")).strip() != "Verified":
            continue
        gate_id = str(row.get("id", "")).strip() or "unknown gate"
        source_revision = row.get("source_revision")
        if (
            not isinstance(source_revision, str)
            or re.fullmatch(r"[0-9a-f]{40}", source_revision) is None
        ):
            errors.append(f"{gate_id}: Verified evidence requires a full source_revision")
        else:
            source_revisions.add(source_revision)
        if not str(row.get("maintainer", "")).strip():
            errors.append(f"{gate_id}: Verified evidence requires a named maintainer")
        errors.extend(
            _bound_record_errors(
                evidence_root,
                row.get("evidence"),
                row.get("evidence_sha256"),
                gate_id,
            )
        )
        if row.get("required") is not True:
            errors.append(f"{gate_id}: every phase 1.3 gate must remain Required")

    if len(source_revisions) > 1:
        errors.append("phase 1.3 gate evidence must bind to one source revision")
    if len(source_revisions) == 1:
        errors.extend(_phase_130_source_revision_errors(next(iter(source_revisions))))

    predecessor = data.get("predecessor_record")
    if not isinstance(predecessor, dict):
        errors.append("phase 1.3 requires a retained v1.2.0 predecessor publication record")
    else:
        predecessor_record = cast(Mapping[str, object], predecessor)
        if predecessor_record.get("published_version") != "v1.2.0":
            errors.append("predecessor_record must identify published_version=v1.2.0")
        if predecessor_record.get("published") is not True:
            errors.append("predecessor_record must confirm v1.2.0 publication")
        for key in ("published_at", "publication_url"):
            if not str(predecessor_record.get(key, "")).strip():
                errors.append(f"predecessor_record.{key} is required")
        errors.extend(
            _bound_record_errors(
                evidence_root,
                predecessor_record.get("release_record"),
                predecessor_record.get("release_record_sha256"),
                "predecessor_record",
            )
        )

    for section, approval_key, reviewer_key in (
        ("maintainer_review", "accepted", "reviewer"),
        ("release_approval", "approved", "approver"),
    ):
        record_value = data.get(section)
        if not isinstance(record_value, dict):
            errors.append(f"phase 1.3 requires [{section}] evidence")
            continue
        record = cast(Mapping[str, object], record_value)
        if record.get(approval_key) is not True:
            errors.append(f"{section}.{approval_key} must be true")
        if not str(record.get(reviewer_key, "")).strip():
            errors.append(f"{section}.{reviewer_key} is required")
        if not str(
            record.get("reviewed_at" if section == "maintainer_review" else "approved_at", "")
        ).strip():
            errors.append(f"{section} timestamp is required")
        errors.extend(
            _bound_record_errors(
                evidence_root,
                record.get(
                    "review_record" if section == "maintainer_review" else "approval_record"
                ),
                record.get(
                    "review_record_sha256"
                    if section == "maintainer_review"
                    else "approval_record_sha256"
                ),
                section,
            )
        )

    artifact_record = data.get("release_artifacts")
    if not isinstance(artifact_record, dict):
        errors.append("phase 1.3 requires a retained release artifact manifest")
    else:
        artifact_mapping = cast(Mapping[str, object], artifact_record)
        errors.extend(
            _bound_record_errors(
                evidence_root,
                artifact_mapping.get("manifest"),
                artifact_mapping.get("manifest_sha256"),
                "release_artifacts",
            )
        )
        if (
            not isinstance(artifact_mapping.get("source_revision"), str)
            or artifact_mapping.get("source_revision") not in source_revisions
        ):
            errors.append("release_artifacts.source_revision must match the verified gate revision")

    contract_name = data.get("planning_contract")
    contract_path: Path | None = None
    if not isinstance(contract_name, str) or not contract_name.strip():
        errors.append("phase 1.3 planning_contract path is required")
    else:
        contract_relative = PurePosixPath(contract_name)
        if (
            contract_relative.is_absolute()
            or ".." in contract_relative.parts
            or "\\" in contract_name
        ):
            errors.append("planning_contract must be a local acceptance-directory path")
        else:
            contract_path = evidence_root / Path(*contract_relative.parts)
            try:
                _ = contract_path.resolve(strict=True).relative_to(evidence_root.resolve())
                contract_data = tomllib.loads(contract_path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                errors.append(f"unable to validate phase 1.3 planning contract: {exc}")
                contract_data = {}
            if contract_data:
                for key in (
                    "freeze_satisfied",
                    "numeric_budgets_frozen",
                    "named_maintainers_assigned",
                ):
                    if contract_data.get(key) is not True:
                        errors.append(f"planning contract {key} must be true")
                api_contract = contract_data.get("api")
                if not isinstance(api_contract, dict):
                    errors.append("planning contract [api] is required")
                else:
                    api_mapping = cast(Mapping[str, object], api_contract)
                    if (
                        api_mapping.get("state") != "Frozen"
                        or api_mapping.get("maturity") != "beta"
                    ):
                        errors.append("planning contract API must be frozen with Beta maturity")
                matrix = contract_data.get("matrix")
                if not isinstance(matrix, dict):
                    errors.append("planning contract [matrix] is required")
                else:
                    matrix_mapping = cast(Mapping[str, object], matrix)
                    if matrix_mapping.get("state") != "Frozen":
                        errors.append("planning contract matrix.state must be Frozen")
                    for key in ("upstream_bounds_verified", "browser_revisions_frozen"):
                        if matrix_mapping.get(key) is not True:
                            errors.append(f"planning contract matrix.{key} must be true")
                budgets = contract_data.get("budgets")
                if not isinstance(budgets, list) or not budgets:
                    errors.append("planning contract must contain measured budgets")
                else:
                    budget_rows = cast(list[object], budgets)
                    for budget_value in budget_rows:
                        if not isinstance(budget_value, dict):
                            errors.append("planning contract budget entries must be tables")
                            continue
                        budget = cast(Mapping[str, object], budget_value)
                        budget_id = str(budget.get("id", "unknown"))
                        if (
                            budget.get("state") != "Measured"
                            or budget.get("threshold_frozen") is not True
                        ):
                            errors.append(
                                f"planning contract budget {budget_id} must be measured and frozen"
                            )
                        if not str(budget.get("unit", "")).strip():
                            errors.append(f"budget {budget_id} requires a threshold unit")
                        limit = budget.get("limit")
                        if not isinstance(limit, (int, float)) or isinstance(limit, bool):
                            errors.append(
                                f"planning contract budget {budget_id} requires a numeric limit"
                            )
                        elif not math.isfinite(float(limit)) or float(limit) <= 0:
                            errors.append(
                                f"planning contract budget {budget_id} requires a positive limit"
                            )
                        sample_count = budget.get("sample_count")
                        if type(sample_count) is not int or sample_count < 1:
                            errors.append(f"budget {budget_id}: sample_count must be positive")
                        errors.extend(
                            _bound_record_errors(
                                evidence_root,
                                budget.get("measurement_evidence"),
                                budget.get("measurement_sha256"),
                                f"planning contract budget {budget_id}",
                            )
                        )
                    budget_ids = tuple(
                        str(cast(Mapping[str, object], budget).get("id", "")).strip()
                        for budget in budget_rows
                        if isinstance(budget, dict)
                    )
                    if budget_ids != PHASE_130_BUDGET_IDS:
                        errors.append(
                            "planning contract budget ids do not match required inventory"
                        )

    dispositions_name = data.get("package_dispositions")
    if not isinstance(dispositions_name, str) or not dispositions_name.strip():
        errors.append("phase 1.3 package_dispositions path is required")
    else:
        dispositions_relative = PurePosixPath(dispositions_name)
        if (
            dispositions_relative.is_absolute()
            or ".." in dispositions_relative.parts
            or "\\" in dispositions_name
        ):
            errors.append("package_dispositions must be a local acceptance-directory path")
        else:
            dispositions_path = evidence_root / Path(*dispositions_relative.parts)
            try:
                _ = dispositions_path.resolve(strict=True).relative_to(evidence_root.resolve())
                dispositions_data = tomllib.loads(dispositions_path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                errors.append(f"unable to validate phase 1.3 package dispositions: {exc}")
                dispositions_data = {}
            if dispositions_data:
                package_rows = dispositions_data.get("package")
                package_count = dispositions_data.get("workspace_package_count")
                has_package_list = isinstance(package_rows, list)
                package_values = cast(list[object], package_rows) if has_package_list else []
                if (
                    not has_package_list
                    or type(package_count) is not int
                    or len(package_values) != package_count
                ):
                    errors.append(
                        "package dispositions must cover the complete workspace inventory"
                    )
                else:
                    package_mappings = [
                        cast(Mapping[str, object], package)
                        for package in package_values
                        if isinstance(package, dict)
                    ]
                    if len(package_mappings) != len(package_values) or any(
                        not str(package.get("id", "")).strip()
                        or not str(package.get("disposition", "")).strip()
                        or not str(package.get("reason", "")).strip()
                        for package in package_mappings
                    ):
                        errors.append(
                            "every package disposition requires id, disposition, and reason"
                        )
                    package_ids = tuple(
                        str(package.get("id", "")).strip() for package in package_mappings
                    )
                    if len(package_ids) != len(set(package_ids)):
                        errors.append("package disposition ids must be unique")
                if dispositions_data.get("maintainer_review_complete") is not True:
                    errors.append("package disposition maintainer review must be complete")

    return errors


def _phase_130_source_revision_errors(source_revision: str) -> list[str]:
    """Bind evidence to a clean code commit with only evidence commits after it.

    Evidence files and the gate itself are committed after CI and artifact
    rehearsal. They cannot be included in the commit whose SHA they record, so
    allow those review records as follow-up commits while rejecting any source
    or build-input changes after the verified code revision.
    """
    try:
        ancestor = subprocess.run(
            ["git", "merge-base", "--is-ancestor", source_revision, "HEAD"],
            cwd=ROOT,
            check=False,
        )
        if ancestor.returncode != 0:
            return ["phase 1.3 evidence source_revision must be an ancestor of the release commit"]
        changed = subprocess.check_output(
            ["git", "diff", "--name-only", f"{source_revision}..HEAD"],
            cwd=ROOT,
            text=True,
        ).splitlines()
        unexpected = sorted(
            path
            for path in changed
            if path not in PHASE_130_EVIDENCE_ONLY_PATHS
            and not path.startswith(PHASE_130_EVIDENCE_ONLY_PREFIX)
        )
        if unexpected:
            return [
                "phase 1.3 source revision predates non-evidence changes: "
                + ", ".join(unexpected[:5])
            ]
        dirty = subprocess.check_output(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=ROOT,
            text=True,
        )
        if dirty.strip():
            return ["phase 1.3 strict release validation requires a clean source tree"]
    except (OSError, subprocess.CalledProcessError):
        return ["phase 1.3 evidence source revision cannot be verified in this checkout"]
    return []


def _validate_phase_130_contract(data: dict[str, object], path: Path, *, strict: bool) -> list[str]:
    """Validate the fixed 1.3.0 gate inventory and release-only conditions."""
    errors: list[str] = []
    rows = data.get("evidence")
    found: tuple[str, ...] = ()
    if isinstance(rows, list):
        evidence_rows = cast(list[object], rows)
        typed_rows = (
            cast(Mapping[str, object], row) for row in evidence_rows if isinstance(row, dict)
        )
        found = tuple(str(row.get("id", "")).strip() for row in typed_rows)
    if found != PHASE_130_EVIDENCE_IDS:
        errors.append(
            f"{path}: phase 1.3 gate order mismatch: {found!r}; expected {PHASE_130_EVIDENCE_IDS!r}"
        )
    if isinstance(rows, list):
        phase_rows = cast(list[object], rows)
        for row_value in phase_rows:
            if not isinstance(row_value, dict):
                continue
            row = cast(Mapping[str, object], row_value)
            if row.get("required") is not True:
                errors.append(f"{row.get('id', 'unknown gate')}: phase 1.3 gates must be Required")
    if data.get("target") != "v1.3.0":
        errors.append(f"{path}: phase 1.3 release target must be v1.3.0")
    if data.get("required_predecessor") != "v1.2.0":
        errors.append(f"{path}: phase 1.3 predecessor must be v1.2.0")
    if strict:
        if data.get("predecessor_satisfied") is not True:
            errors.append(f"{path}: v1.2.0 predecessor evidence must be satisfied")
        if data.get("stage_1_entry_satisfied") is not True:
            errors.append(f"{path}: stage_1_entry_satisfied must be true before release")
        if data.get("release_cut_satisfied") is not True:
            errors.append(f"{path}: release_cut_satisfied must be true before v1.3.0 publication")
        if data.get("candidate_api_maturity") != "beta":
            errors.append(f"{path}: new phase 1.3 API maturity must remain beta")
        if not isinstance(rows, list) or any(
            not isinstance(row, dict)
            or str(cast(Mapping[str, object], row).get("state", "")).strip() != "Verified"
            for row in cast(list[object], rows)
        ):
            errors.append(
                f"{path}: every required phase 1.3 gate must be Verified before publication"
            )
        if data.get("status") != "ReleaseApproved":
            errors.append(f"{path}: status must be ReleaseApproved before publication")
        errors.extend(
            _validate_phase_130_release_records(
                data,
                cast(list[object], rows) if isinstance(rows, list) else [],
                path,
            )
        )
    return errors


def _is_alpha_package(project: dict[str, object]) -> bool:
    classifiers = project.get("classifiers")
    if not isinstance(classifiers, list):
        return False
    return any("Development Status :: 3 - Alpha" in str(c) for c in classifiers)


def _is_independent_version_package(project: dict[str, object]) -> bool:
    """True when the package versions independently of the Beta flagship train.

    Alpha satellites always version independently. Beta packages on the ``0.1.x``
    satellite line (charts/native after 0.28 graduation) also stay independent of
    the ``0.N.0`` train tag. ``fastapi-workbench`` 1.x versions independently per D-058.
    ``hedron-mcp`` ``0.2.x`` Beta is an independent satellite per D-060 / RFC-0065.
    ``hedron-charts`` ``0.2.x`` Beta is an independent satellite per D-066 / RFC-0069.
    ``hedron-sample-kit`` / ``hedron-notebook`` / ``hedron-sim`` ``0.2.x`` Beta are
    independent satellites per D-093 / RFC-0081. ``hedron-posit`` ``0.67.x`` is an
    independent patch satellite. ``hedron-docs`` ``0.3.x`` is an independent W3 documentation
    compiler line. ``edron`` is a separately released ``0.2.x`` Beta facade per RFC-0094.
    """
    if _is_alpha_package(project):
        return True
    name = str(project.get("name", ""))
    if name in {
        "fastapi-workbench",
        "hedron-mcp",
        "hedron-gradio",
        "hedron-charts",
        "hedron-sample-kit",
        "hedron-notebook",
        "hedron-sim",
        "edron-sim",
        "hedron-docs",
        "hedron-posit",
        "edron",
    }:
        return True
    version = str(project.get("version", ""))
    return version.startswith("0.1.")


def check_packages(tag_version: str) -> list[str]:
    errors: list[str] = []
    if not (ROOT / "LICENSE").is_file():
        errors.append("missing root LICENSE (required before public publication)")

    workspace = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    workspace_version = str(workspace["version"])
    if workspace_version != tag_version:
        errors.append(f"hedron-workspace: version {workspace_version!r} != tag {tag_version!r}")

    for pyproject in sorted((ROOT / "packages").glob("*/pyproject.toml")):
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        project = data["project"]
        name = str(project["name"])
        version = str(project["version"])
        independent = _is_independent_version_package(project)
        # Independent satellites (Alpha or 0.1.x Beta) version off the flagship train.
        expected = version if independent else tag_version
        if not independent and version != tag_version:
            errors.append(f"{name}: package version {version!r} != tag {tag_version!r}")
        if "license" not in project and "license-files" not in project:
            errors.append(f"{name}: [project].license (or license-files) is required")
        pkg_dir = pyproject.parent
        module_name = name.replace("-", "_")
        init = pkg_dir / "src" / module_name / "__init__.py"
        if not init.is_file():
            errors.append(f"{name}: primary __init__ missing at {init.relative_to(ROOT)}")
            continue
        init_text = init.read_text(encoding="utf-8")
        match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', init_text, re.M)
        resolved_version = match.group(1) if match else None
        if resolved_version is None:
            delegated = re.search(r"^__version__\s*=\s*([A-Za-z_]\w*)", init_text, re.M)
            version_module = init.with_name("_version.py")
            if delegated and version_module.is_file():
                constant_name = re.escape(delegated.group(1))
                constant = re.search(
                    rf'^{constant_name}\s*=\s*["\']([^"\']+)["\']',
                    version_module.read_text(encoding="utf-8"),
                    re.M,
                )
                if constant:
                    resolved_version = constant.group(1)
        if resolved_version is None:
            errors.append(f"{name}: __version__ not found in {init}")
        elif resolved_version != expected:
            errors.append(f"{name}: __version__ {resolved_version!r} != package {expected!r}")
        for plugin in init.parent.rglob("*.py"):
            plugin_source = plugin.read_text(encoding="utf-8")
            plugin_match = re.search(
                r"PLUGIN_META\s*=\s*PluginMeta\(.*?\bversion\s*=\s*(?:[\"']([^\"']+)[\"']|([A-Za-z_]\w*))",
                plugin_source,
                re.S,
            )
            plugin_version = plugin_match.group(1) if plugin_match else None
            if plugin_match and plugin_version is None:
                version_module = plugin.with_name("_version.py")
                if version_module.is_file():
                    constant_name = re.escape(str(plugin_match.group(2)))
                    constant = re.search(
                        rf'^{constant_name}\s*=\s*["\']([^"\']+)["\']',
                        version_module.read_text(encoding="utf-8"),
                        re.M,
                    )
                    if constant:
                        plugin_version = constant.group(1)
            if plugin_match and plugin_version is None:
                errors.append(
                    f"{name}: PluginMeta version cannot be resolved in "
                    f"{plugin.relative_to(pkg_dir)}"
                )
            elif plugin_version is not None and plugin_version != version:
                errors.append(
                    f"{name}: PluginMeta version {plugin_version!r} in "
                    f"{plugin.relative_to(pkg_dir)} != package {version!r}"
                )
        changelog = pkg_dir / "CHANGELOG.md"
        if not changelog.is_file():
            errors.append(f"{name}: missing CHANGELOG.md")
        elif f"[{expected}]" not in changelog.read_text(encoding="utf-8"):
            errors.append(f"{name}: CHANGELOG.md lacks [{expected}] section")
    return errors


def _command_tokens(command: str) -> list[str]:
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()


def _referenced_repo_paths(command: str) -> list[str]:
    """Return scripts/ or tests/ path tokens that should exist on disk."""
    paths: list[str] = []
    for token in _command_tokens(command):
        if token.startswith("scripts/") or token.startswith("tests/"):
            paths.append(token)
    return paths


def _is_suite_command(command: str) -> bool:
    tokens = _command_tokens(command)
    if not tokens:
        return False
    joined = " ".join(tokens)
    if "ci_checks.sh" in joined:
        return True
    if tokens[0] in {"pytest", "bash"}:
        return True
    if len(tokens) >= 2 and tokens[0] == "python" and tokens[1] == "-m" and "pytest" in tokens:
        return True
    return any(t.startswith("verify_pkg_") and t.endswith(".py") for t in tokens)


def _is_executable_ssot_command(command: str) -> bool:
    """True for ``python scripts/check_*.py`` style commands safe to run inline."""
    tokens = _command_tokens(command)
    if len(tokens) < 2 or tokens[0] != "python":
        return False
    script = tokens[1]
    if not script.startswith("scripts/") or not script.endswith(".py"):
        return False
    name = Path(script).name
    if name in _RECURSIVE_SCRIPT_NAMES:
        return False
    return name.startswith("check_")


def _validate_verified_command(eid: str, command: str, ci_job: str) -> list[str]:
    errors: list[str] = []
    if not command:
        errors.append(f"{eid}: Verified entries require a named command")
        return errors
    if not ci_job:
        errors.append(f"{eid}: Verified entries require ci_job (CI attestation)")
    elif ci_job not in KNOWN_CI_JOBS:
        errors.append(f"{eid}: unknown ci_job {ci_job!r} (expected one of {sorted(KNOWN_CI_JOBS)})")

    for rel in _referenced_repo_paths(command):
        target = ROOT / rel
        if not target.exists():
            errors.append(f"{eid}: command references missing path {rel}")

    if _is_suite_command(command):
        checks = (ROOT / "scripts" / "ci_checks.sh").read_text(encoding="utf-8")
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        release_wf = ROOT / ".github" / "workflows" / "release.yml"
        attested = False
        if ci_job:
            if f"cmd_{ci_job}" in checks or f"ci_checks.sh {ci_job}" in workflow:
                attested = True
            if ci_job == "release" and release_wf.is_file():
                attested = True
        if ci_job and not attested:
            errors.append(
                f"{eid}: suite command ci_job={ci_job!r} is not attested in "
                "scripts/ci_checks.sh, .github/workflows/ci.yml, or release.yml"
            )
        # pytest-only suite commands must be owned by the test job.
        tokens = _command_tokens(command)
        if "pytest" in tokens and ci_job and ci_job != "test":
            errors.append(f"{eid}: pytest suite commands require ci_job=test")
    return errors


def check_evidence_manifest(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"missing evidence manifest: {path}"]
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    rows = data.get("evidence")
    if not isinstance(rows, list) or not rows:
        return [f"{path}: [[evidence]] entries required"]
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            errors.append(f"{path}: evidence row must be a table")
            continue
        eid = str(row.get("id", "")).strip()
        state = str(row.get("state", "")).strip()
        command = str(row.get("command", "")).strip()
        owner = str(row.get("owner", "")).strip()
        ci_job = str(row.get("ci_job", "")).strip()
        if not eid:
            errors.append(f"{path}: evidence id is required")
            continue
        if eid in seen:
            errors.append(f"{path}: duplicate evidence id {eid}")
        seen.add(eid)
        if state not in {"Planned", "Implemented", "Verified", "Deferred", "Blocked"}:
            errors.append(f"{eid}: invalid state {state!r}")
        if not owner:
            errors.append(f"{eid}: owner is required")
        if state == "Verified":
            errors.extend(_validate_verified_command(eid, command, ci_job))
        if state == "Deferred":
            if not str(row.get("rationale", "")).strip():
                errors.append(f"{eid}: Deferred entries require rationale")
            if not str(row.get("destination", "")).strip():
                errors.append(f"{eid}: Deferred entries require destination")
        if state in {"Blocked", "Implemented", "Planned"}:
            errors.append(
                f"{eid}: state {state!r} does not close the release gate "
                "(use Verified or Deferred with ownership)"
            )
    if data.get("phase") == "1.2":
        found = tuple(str(row.get("id", "")).strip() for row in rows if isinstance(row, dict))
        if found != PHASE_120_EVIDENCE_IDS:
            errors.append(
                f"{path}: phase 1.2 gate order mismatch: {found!r}; "
                f"expected {PHASE_120_EVIDENCE_IDS!r}"
            )
        if data.get("target") != "v1.2.0":
            errors.append(f"{path}: phase 1.2 release target must be v1.2.0")
        if data.get("support_policy_amendment_accepted") is not True:
            errors.append(f"{path}: phase 1.2 support-policy amendment must be accepted")
        if data.get("stage_1_entry_satisfied") is not True:
            errors.append(f"{path}: phase 1.2 implementation entry must be satisfied")
        if data.get("release_cut_satisfied") is not True:
            errors.append(f"{path}: release_cut_satisfied must be true before v1.2.0 publication")
        if any(
            not isinstance(row, dict) or str(row.get("state", "")).strip() != "Verified"
            for row in rows
        ):
            errors.append(
                f"{path}: every required phase 1.2 gate must be Verified before publication"
            )
    if data.get("phase") == "1.3":
        errors.extend(_validate_phase_130_contract(data, path, strict=True))
    return errors


def execute_verified_ssot_commands(path: Path) -> list[str]:
    """Run Verified ``python scripts/check_*.py`` commands from the manifest.

    Suite commands (pytest / ci_checks / verify_pkg) are attested via ``ci_job``
    and path checks — not re-executed here (avoids recursion and hour-long nests).
    """
    errors: list[str] = []
    if not path.is_file():
        return [f"missing evidence manifest: {path}"]
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    rows = data.get("evidence")
    if not isinstance(rows, list):
        return [f"{path}: [[evidence]] entries required"]
    executed = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("state", "")).strip() != "Verified":
            continue
        eid = str(row.get("id", "")).strip()
        command = str(row.get("command", "")).strip()
        if not _is_executable_ssot_command(command):
            continue
        tokens = _command_tokens(command)
        # Prefer the active interpreter for portability inside uv/venv.
        argv = [sys.executable, *tokens[1:]]
        print("+", *argv)
        try:
            subprocess.check_call(argv, cwd=ROOT)
        except subprocess.CalledProcessError as exc:
            errors.append(f"{eid}: command failed ({exc.returncode}): {command}")
        else:
            executed += 1
    if executed == 0:
        # Not fatal for older manifests with only suite commands — path/ci_job
        # validation still applies. Warn for visibility.
        print("note: no executable SSOT Verified commands in manifest", file=sys.stderr)
    return errors


def check_evidence_manifest_lenient(path: Path) -> list[str]:
    """Validate shape without requiring Verified/Deferred closure."""
    errors: list[str] = []
    if not path.is_file():
        return [f"missing evidence manifest: {path}"]
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    rows = data.get("evidence")
    if not isinstance(rows, list) or not rows:
        return [f"{path}: [[evidence]] entries required"]
    if data.get("phase") == "1.3":
        errors.extend(_validate_phase_130_contract(data, path, strict=False))
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            errors.append(f"{path}: evidence row must be a table")
            continue
        eid = str(row.get("id", "")).strip()
        state = str(row.get("state", "")).strip()
        owner = str(row.get("owner", "")).strip()
        command = str(row.get("command", "")).strip()
        ci_job = str(row.get("ci_job", "")).strip()
        if not eid:
            errors.append(f"{path}: evidence id is required")
            continue
        if eid in seen:
            errors.append(f"{path}: duplicate evidence id {eid}")
        seen.add(eid)
        if state not in {"Planned", "Implemented", "Verified", "Deferred", "Blocked"}:
            errors.append(f"{eid}: invalid state {state!r}")
        if not owner:
            errors.append(f"{eid}: owner is required")
        if state == "Verified":
            errors.extend(_validate_verified_command(eid, command, ci_job))
        if state == "Deferred":
            if not str(row.get("rationale", "")).strip():
                errors.append(f"{eid}: Deferred entries require rationale")
            if not str(row.get("destination", "")).strip():
                errors.append(f"{eid}: Deferred entries require destination")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="Package version without the leading v")
    parser.add_argument(
        "--evidence-manifest",
        type=Path,
        default=None,
        help="Path to release-gate evidence TOML (default: version-selected manifest)",
    )
    parser.add_argument(
        "--allow-planned",
        action="store_true",
        help="Accept Planned/Implemented rows (scaffold / in-progress gates)",
    )
    parser.add_argument(
        "--skip-evidence",
        action="store_true",
        help="Skip evidence manifest checks (metadata-only)",
    )
    parser.add_argument(
        "--execute-verified",
        action="store_true",
        help=(
            "Execute Verified python scripts/check_*.py commands from the manifest "
            "(suite/verify_pkg commands are attested via ci_job, not re-run)"
        ),
    )
    args = parser.parse_args()
    # Always verify package metadata matches the requested train version.
    # --allow-planned only relaxes evidence closure (Planned/Implemented rows OK).
    errors = check_packages(args.version)
    if not args.skip_evidence:
        manifest = args.evidence_manifest or evidence_manifest_for(args.version)
        if args.allow_planned:
            errors.extend(check_evidence_manifest_lenient(manifest))
        else:
            errors.extend(check_evidence_manifest(manifest))
        if args.execute_verified and not errors:
            errors.extend(execute_verified_ssot_commands(manifest))
    if not (ROOT / "LICENSE").is_file():
        errors.append("missing root LICENSE (required before public publication)")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"ok: release gate for {args.version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
