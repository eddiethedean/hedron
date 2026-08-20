"""CLI entry for the conformance kit."""

from __future__ import annotations

import argparse
import json

from hedron_conformance import __version__
from hedron_conformance.compile import compile_suite
from hedron_conformance.profiles import load_profile_registry, profile_suite_digest, suite_digest
from hedron_conformance.report import build_result_envelope, to_junit, to_sarif
from hedron_conformance.runner import run_kit
from hedron_conformance.schema import fixture_schema_dict, load_bundled_fixtures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="hedron-conformance")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run bundled fixtures against the reference evaluator")
    run_p.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON report",
    )
    run_p.add_argument(
        "--junit",
        action="store_true",
        help="Emit JUnit XML after the run",
    )
    run_p.add_argument(
        "--sarif",
        action="store_true",
        help="Emit SARIF JSON after the run",
    )
    run_p.add_argument(
        "--envelope",
        action="store_true",
        help="Emit a signed-ish result envelope after the run",
    )

    sub.add_parser("schema", help="Print the ConformanceFixture JSON Schema")
    sub.add_parser("list", help="List bundled fixture ids")
    sub.add_parser("compile", help="Compile/validate the bundled fixture suite")
    sub.add_parser("profiles", help="List profile registry ids and suite digests")

    args = parser.parse_args(argv)
    if args.command == "schema":
        print(json.dumps(fixture_schema_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "list":
        for fixture in load_bundled_fixtures():
            print(f"{fixture.id}\t{fixture.capability.value}\t{fixture.contract_version}")
        return 0
    if args.command == "compile":
        report = compile_suite(load_bundled_fixtures())
        payload = {"ok": report.ok, "errors": list(report.errors)}
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if report.ok else 1
    if args.command == "profiles":
        registry = load_profile_registry()
        rows = [
            {
                "id": profile.id,
                "capabilities": sorted(cap.value for cap in profile.capabilities),
                "suite_digest": profile_suite_digest(profile.id),
            }
            for profile in registry.profiles
        ]
        print(json.dumps(rows, indent=2, sort_keys=True))
        return 0
    if args.command == "run":
        report = run_kit()
        if args.json:
            payload = {
                "ok": report.ok,
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
                "capabilities": {
                    cap.value: {"passed": cr.passed, "failed": cr.failed, "ok": cr.ok}
                    for cap, cr in report.by_capability.items()
                },
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            for r in report.results:
                status = "PASS" if r.passed else "FAIL"
                print(f"{status}\t{r.fixture_id}\t{r.capability.value}\t{r.contract_version}")
                if r.detail:
                    print(f"  {r.detail}")
            summary = (
                f"{sum(1 for r in report.results if r.passed)}/"
                f"{len(report.results)} fixtures passed"
            )
            print(summary)
        if args.envelope:
            digest = suite_digest(load_bundled_fixtures())
            print(
                json.dumps(
                    build_result_envelope(report, manifest_digest=digest),
                    indent=2,
                    sort_keys=True,
                )
            )
        if args.junit:
            print(to_junit(report))
        if args.sarif:
            print(json.dumps(to_sarif(report), indent=2, sort_keys=True))
        return 0 if report.ok else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
