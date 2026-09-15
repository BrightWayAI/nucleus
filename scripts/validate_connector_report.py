#!/usr/bin/env python3
"""Validate sanitized evidence from live Nucleus connector probes.

The live calls happen inside a host that owns the connector authorization. This
validator deliberately accepts metadata-only evidence and rejects raw payload fields.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "connector-tests" / "plan.json"
HOSTS = {"claude", "chatgpt", "codex", "direct-mcp"}
STATUSES = {"pass", "fail", "skip", "not-run"}
FORBIDDEN_KEYS = {
    "body",
    "content",
    "email",
    "message",
    "name",
    "payload",
    "raw",
    "subject",
    "text",
    "title",
    "value",
}


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON {path}: {exc}") from exc


def validate_report(
    plan: dict[str, object],
    report: dict[str, object],
    *,
    expected_release: str | None = None,
    required_profile: str | None = None,
) -> list[str]:
    errors: list[str] = []
    if report.get("schemaVersion") != 1:
        errors.append("report.schemaVersion must be 1")
    release = report.get("release")
    if not isinstance(release, str) or not release.strip():
        errors.append("report.release must be a non-empty string")
    elif expected_release and release != expected_release:
        errors.append(f"report.release is {release!r}; expected {expected_release!r}")
    host = report.get("host")
    if host not in HOSTS:
        errors.append(f"report.host must be one of {sorted(HOSTS)}")
    run_at = report.get("runAt")
    if not isinstance(run_at, str) or not re.match(r"^\d{4}-\d{2}-\d{2}T", run_at):
        errors.append("report.runAt must be an ISO-8601 timestamp")

    profiles = plan.get("profiles", {})
    profile = required_profile or report.get("profile")
    if not isinstance(profiles, dict) or profile not in profiles:
        errors.append(f"unknown connector profile: {profile!r}")
        required: set[str] = set()
    else:
        raw_required = profiles[profile]
        required = set(raw_required if isinstance(raw_required, list) else [])

    connector_rows = plan.get("connectors", [])
    known = {
        row.get("id")
        for row in connector_rows
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    results = report.get("results")
    if not isinstance(results, list):
        errors.append("report.results must be an array")
        return errors

    seen: set[str] = set()
    by_id: dict[str, dict[str, object]] = {}
    allowed_result_keys = {"id", "status", "tool", "latencyMs", "observation", "errorCode"}
    allowed_observation_keys = {"recordCount", "contentTypes", "topLevelKeys"}
    for index, item in enumerate(results):
        label = f"results[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        extra = set(item) - allowed_result_keys
        forbidden = {key for key in extra if key.lower() in FORBIDDEN_KEYS}
        if extra:
            errors.append(f"{label} has unsupported fields: {sorted(extra)}")
        if forbidden:
            errors.append(f"{label} includes raw-data fields: {sorted(forbidden)}")
        connector_id = item.get("id")
        if connector_id not in known:
            errors.append(f"{label}.id is not in the connector plan: {connector_id!r}")
            continue
        if connector_id in seen:
            errors.append(f"duplicate connector result: {connector_id}")
        seen.add(str(connector_id))
        by_id[str(connector_id)] = item
        status = item.get("status")
        if status not in STATUSES:
            errors.append(f"{label}.status must be one of {sorted(STATUSES)}")
        if status == "pass" and not item.get("tool"):
            errors.append(f"{label}.tool is required for a passing live probe")
        latency = item.get("latencyMs")
        if latency is not None and (not isinstance(latency, int) or latency < 0):
            errors.append(f"{label}.latencyMs must be a non-negative integer or null")
        observation = item.get("observation")
        if observation is not None:
            if not isinstance(observation, dict):
                errors.append(f"{label}.observation must be an object or null")
            else:
                observation_extra = set(observation) - allowed_observation_keys
                if observation_extra:
                    errors.append(
                        f"{label}.observation has unsupported fields: {sorted(observation_extra)}"
                    )
                count = observation.get("recordCount")
                if count is not None and (not isinstance(count, int) or count < 0):
                    errors.append(f"{label}.observation.recordCount must be non-negative")
                for key in ("contentTypes", "topLevelKeys"):
                    value = observation.get(key)
                    if value is not None and not (
                        isinstance(value, list) and all(isinstance(entry, str) for entry in value)
                    ):
                        errors.append(f"{label}.observation.{key} must be an array of strings")

    for connector_id in sorted(required):
        result = by_id.get(connector_id)
        if not result:
            errors.append(f"required connector has no result: {connector_id}")
        elif result.get("status") != "pass":
            errors.append(
                f"required connector did not pass: {connector_id} ({result.get('status')})"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--release")
    parser.add_argument("--profile")
    args = parser.parse_args()
    try:
        plan = load_json(args.plan)
        report = load_json(args.report)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if not isinstance(plan, dict) or not isinstance(report, dict):
        print("ERROR: plan and report must both be JSON objects", file=sys.stderr)
        return 1
    errors = validate_report(
        plan,
        report,
        expected_release=args.release,
        required_profile=args.profile,
    )
    if errors:
        print("Connector report validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        f"Connector report passed: host={report['host']} profile={args.profile or report['profile']} "
        f"release={report['release']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
