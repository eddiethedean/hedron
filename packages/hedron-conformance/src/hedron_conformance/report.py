"""Signed-ish result envelopes, JUnit/SARIF converters, offline bundles."""

from __future__ import annotations

import hashlib
import hmac
import json
import xml.etree.ElementTree as ET
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any, cast

from hedron_conformance.runner import KitReport
from hedron_conformance.schema import CONTRACT_VERSION

ENVELOPE_VERSION = "1.0.0"


def _kit_report_dict(report: KitReport) -> dict[str, Any]:
    return {
        "ok": report.ok,
        "contract_version": CONTRACT_VERSION,
        "results": [
            {
                "fixture_id": r.fixture_id,
                "contract_version": r.contract_version,
                "capability": r.capability.value,
                "passed": r.passed,
                "detail": r.detail,
            }
            for r in report.results
        ],
    }


def _canonical_json(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )


def build_result_envelope(
    report: KitReport,
    *,
    manifest_digest: str,
    key: bytes | str | None = None,
    kit_id: str = "hedron-conformance",
) -> dict[str, Any]:
    """Build a deterministic offline-capable result envelope.

    Provenance is HMAC-SHA256 when ``key`` is provided; otherwise SHA-256 over
    the canonical kit report + manifest digest (signed-ish, offline).
    """
    body = _kit_report_dict(report)
    body["manifest_digest"] = manifest_digest
    body["kit_id"] = kit_id
    body["envelope_version"] = ENVELOPE_VERSION
    canonical = _canonical_json(body)
    if key is None:
        algorithm = "sha256"
        digest = hashlib.sha256(canonical).hexdigest()
    else:
        algorithm = "hmac-sha256"
        secret = key.encode("utf-8") if isinstance(key, str) else key
        digest = hmac.new(secret, canonical, hashlib.sha256).hexdigest()
    return {
        "envelope_version": ENVELOPE_VERSION,
        "kit_id": kit_id,
        "contract_version": CONTRACT_VERSION,
        "manifest_digest": manifest_digest,
        "ok": report.ok,
        "report": body,
        "provenance": {
            "algorithm": algorithm,
            "digest": digest,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    }


def to_junit(report: KitReport, *, suite_name: str = "hedron-conformance") -> str:
    """Convert a kit report to JUnit XML (string)."""
    testsuite = ET.Element(
        "testsuite",
        name=suite_name,
        tests=str(len(report.results)),
        failures=str(sum(1 for r in report.results if not r.passed)),
        errors="0",
    )
    for result in report.results:
        case = ET.SubElement(
            testsuite,
            "testcase",
            classname=result.capability.value,
            name=result.fixture_id,
        )
        if not result.passed:
            failure = ET.SubElement(case, "failure", message=result.detail or "failed")
            failure.text = result.detail
    return ET.tostring(testsuite, encoding="unicode")


def to_sarif(report: KitReport, *, tool_name: str = "hedron-conformance") -> dict[str, Any]:
    """Convert a kit report to a minimal SARIF 2.1.0 document."""
    results: list[dict[str, Any]] = []
    for item in report.results:
        if item.passed:
            continue
        results.append(
            {
                "ruleId": f"fixture/{item.fixture_id}",
                "level": "error",
                "message": {"text": item.detail or f"{item.fixture_id} failed"},
                "properties": {
                    "capability": item.capability.value,
                    "contract_version": item.contract_version,
                },
            }
        )
    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": tool_name,
                        "informationUri": "https://github.com/eddiethedean/hedron",
                        "rules": [],
                    }
                },
                "results": results,
                "properties": {
                    "ok": report.ok,
                    "contract_version": CONTRACT_VERSION,
                    "fixture_count": len(report.results),
                },
            }
        ],
    }


def offline_bundle_manifest(
    *,
    envelope: Mapping[str, Any],
    junit_xml: str,
    sarif: Mapping[str, Any],
    extra_files: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Deterministic offline bundle inventory (paths + digests)."""
    files = {
        "result-envelope.json": hashlib.sha256(_canonical_json(dict(envelope))).hexdigest(),
        "junit.xml": hashlib.sha256(junit_xml.encode("utf-8")).hexdigest(),
        "results.sarif.json": hashlib.sha256(_canonical_json(dict(sarif))).hexdigest(),
    }
    for name in extra_files or ():
        files[name] = hashlib.sha256(name.encode("utf-8")).hexdigest()
    return {
        "bundle_version": "1.0.0",
        "contract_version": CONTRACT_VERSION,
        "offline": True,
        "files": files,
        "manifest_digest": str(envelope.get("manifest_digest", "")),
    }


def verify_envelope_digest(
    envelope: Mapping[str, Any],
    *,
    key: bytes | str | None = None,
) -> bool:
    """Recompute provenance digest for the embedded report body."""
    body = envelope.get("report")
    if not isinstance(body, dict):
        return False
    canonical = _canonical_json(cast(dict[str, Any], body))
    provenance = cast(dict[str, Any], envelope.get("provenance") or {})
    expected = str(provenance.get("digest", ""))
    algorithm = str(provenance.get("algorithm", ""))
    if algorithm == "hmac-sha256":
        if key is None:
            return False
        secret = key.encode("utf-8") if isinstance(key, str) else key
        actual = hmac.new(secret, canonical, hashlib.sha256).hexdigest()
    else:
        actual = hashlib.sha256(canonical).hexdigest()
    return hmac.compare_digest(actual, expected)


__all__ = [
    "ENVELOPE_VERSION",
    "build_result_envelope",
    "offline_bundle_manifest",
    "to_junit",
    "to_sarif",
    "verify_envelope_digest",
]
