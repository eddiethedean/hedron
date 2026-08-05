"""CLI entry for the conformance kit."""

from __future__ import annotations

import argparse
import json

from hedron_conformance import __version__
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

    sub.add_parser("schema", help="Print the ConformanceFixture JSON Schema")
    sub.add_parser("list", help="List bundled fixture ids")

    args = parser.parse_args(argv)
    if args.command == "schema":
        print(json.dumps(fixture_schema_dict(), indent=2, sort_keys=True))
        return 0
    if args.command == "list":
        for fixture in load_bundled_fixtures():
            print(f"{fixture.id}\t{fixture.capability.value}\t{fixture.contract_version}")
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
        return 0 if report.ok else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
