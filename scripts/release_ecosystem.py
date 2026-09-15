#!/usr/bin/env python3
"""Create and validate coordinated, commit-pinned Nucleus releases."""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

from catalog import PLUGIN_REPOSITORIES
from validate_connector_report import load_json, validate_report


ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = ROOT.parent
RELEASES_ROOT = ROOT / "releases"
PLAN_PATH = ROOT / "connector-tests" / "plan.json"
RELEASE_ID = re.compile(r"^[0-9]{4}\.[0-9]{2}\.[0-9]+(?:[-.][0-9A-Za-z]+)*$")
SHA = re.compile(r"^[0-9a-f]{40}$")
PLUGINS = [(name, repo) for name, repo, _ in PLUGIN_REPOSITORIES]


def dump_json(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, text=True, capture_output=True, check=False
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed in {repo}: {detail}")
    return result.stdout.strip()


def manifest_at(repo: Path, revision: str) -> dict[str, object]:
    raw = git(repo, "show", f"{revision}:.codex-plugin/plugin.json")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise RuntimeError(f"invalid plugin manifest at {repo.name}@{revision}")
    return value


def release_dir(release_id: str) -> Path:
    if not RELEASE_ID.match(release_id):
        raise ValueError(
            "release ID must look like 2026.09.0 or 2026.09.0-rc.1"
        )
    return RELEASES_ROOT / release_id


def build_snapshot(release_id: str, revision: str, allow_dirty: bool) -> dict[str, object]:
    rows = []
    for plugin_name, repo_name in PLUGINS:
        repo = LAB_ROOT / repo_name
        if not repo.is_dir():
            raise RuntimeError(f"missing sibling repository: {repo}")
        dirty = git(repo, "status", "--porcelain")
        if dirty and not allow_dirty:
            raise RuntimeError(
                f"{repo_name} has uncommitted changes; commit or pass --allow-dirty "
                "when deliberately snapshotting another revision"
            )
        commit = git(repo, "rev-parse", revision)
        if not SHA.match(commit):
            raise RuntimeError(f"invalid commit for {repo_name}: {commit}")
        manifest = manifest_at(repo, commit)
        expected_name = plugin_name
        if manifest.get("name") != expected_name:
            raise RuntimeError(
                f"manifest name mismatch for {repo_name}: {manifest.get('name')!r}"
            )
        version = manifest.get("version")
        if not isinstance(version, str) or not version:
            raise RuntimeError(f"missing version for {repo_name}@{commit}")
        rows.append(
            {
                "name": plugin_name,
                "repository": f"https://github.com/BrightWayAI/{repo_name}.git",
                "version": version,
                "commit": commit,
            }
        )
    return {
        "schemaVersion": 1,
        "release": release_id,
        "status": "candidate",
        "createdAt": dt.date.today().isoformat(),
        "plugins": rows,
        "requiredConnectorProfiles": [
            {"host": "claude", "profile": "operator"},
            {"host": "chatgpt", "profile": "operator"},
        ],
        "connectorEvidence": [],
    }


def native_marketplace(snapshot: dict[str, object]) -> dict[str, object]:
    rolling = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
    if not isinstance(rolling, dict):
        raise RuntimeError("native marketplace is not an object")
    metadata = {
        row["name"]: row
        for row in snapshot["plugins"]
        if isinstance(row, dict) and isinstance(row.get("name"), str)
    }
    value = copy.deepcopy(rolling)
    for entry in value.get("plugins", []):
        row = metadata[entry["name"]]
        entry["source"]["url"] = row["repository"]
        entry["source"]["sha"] = row["commit"]
    value["interface"]["displayName"] = f"Nucleus {snapshot['release']}"
    return value


def claude_marketplace(snapshot: dict[str, object]) -> dict[str, object]:
    rolling = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    if not isinstance(rolling, dict):
        raise RuntimeError("Claude marketplace is not an object")
    versions = {
        ("claude-cortex" if row["name"] == "cortex" else row["name"]): row["version"]
        for row in snapshot["plugins"]
        if isinstance(row, dict)
    }
    value = copy.deepcopy(rolling)
    for entry in value.get("plugins", []):
        entry["version"] = versions[entry["name"]]
    value["description"] = (
        f"Nucleus {snapshot['release']} coordinated catalog. Commit pins are authoritative "
        "in release.json and the native OpenAI marketplace."
    )
    return value


def validate_native_marketplace(
    snapshot: dict[str, object], marketplace: object
) -> list[str]:
    """Validate immutable OpenAI pins without consulting the rolling catalog."""
    if not isinstance(marketplace, dict):
        return ["pinned native marketplace must be an object"]
    plugins = marketplace.get("plugins")
    rows = snapshot.get("plugins")
    if not isinstance(plugins, list) or not isinstance(rows, list):
        return ["pinned native marketplace plugins must be an array"]
    errors: list[str] = []
    expected_names = [row.get("name") for row in rows if isinstance(row, dict)]
    actual_names = [entry.get("name") for entry in plugins if isinstance(entry, dict)]
    if actual_names != expected_names:
        errors.append("pinned native marketplace names/order differ from release.json")
    rows_by_name = {
        row["name"]: row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("name"), str)
    }
    for entry in plugins:
        if not isinstance(entry, dict):
            errors.append("pinned native marketplace entry must be an object")
            continue
        name = entry.get("name")
        row = rows_by_name.get(name)
        source = entry.get("source")
        if row is None or not isinstance(source, dict):
            errors.append(f"invalid pinned native marketplace entry: {name}")
            continue
        if source.get("url") != row.get("repository"):
            errors.append(f"native repository differs from release.json: {name}")
        if source.get("sha") != row.get("commit"):
            errors.append(f"native commit pin differs from release.json: {name}")
    return errors


def validate_claude_marketplace(
    snapshot: dict[str, object], marketplace: object
) -> list[str]:
    """Validate the frozen Claude catalog against release.json only."""
    if not isinstance(marketplace, dict):
        return ["Claude release catalog must be an object"]
    plugins = marketplace.get("plugins")
    rows = snapshot.get("plugins")
    if not isinstance(plugins, list) or not isinstance(rows, list):
        return ["Claude release catalog plugins must be an array"]
    errors: list[str] = []
    expected_names = [
        "claude-cortex" if row.get("name") == "cortex" else row.get("name")
        for row in rows
        if isinstance(row, dict)
    ]
    actual_names = [entry.get("name") for entry in plugins if isinstance(entry, dict)]
    if actual_names != expected_names:
        errors.append("Claude release catalog names/order differ from release.json")
    rows_by_claude_name = {
        ("claude-cortex" if row["name"] == "cortex" else row["name"]): row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("name"), str)
    }
    for entry in plugins:
        if not isinstance(entry, dict):
            errors.append("Claude release catalog entry must be an object")
            continue
        name = entry.get("name")
        row = rows_by_claude_name.get(name)
        source = entry.get("source")
        if row is None or not isinstance(source, dict):
            errors.append(f"invalid Claude release catalog entry: {name}")
            continue
        expected_repo = str(row.get("repository", ""))
        expected_repo = expected_repo.removeprefix("https://github.com/").removesuffix(".git")
        if source.get("repo") != expected_repo:
            errors.append(f"Claude repository differs from release.json: {name}")
        if entry.get("version") != row.get("version"):
            errors.append(f"Claude version differs from release.json: {name}")
    return errors


def write_snapshot(snapshot: dict[str, object]) -> Path:
    target = release_dir(str(snapshot["release"]))
    if target.exists():
        raise RuntimeError(f"release already exists: {target}")
    (target / ".agents" / "plugins").mkdir(parents=True)
    (target / ".claude-plugin").mkdir(parents=True)
    (target / "release.json").write_text(dump_json(snapshot))
    (target / ".agents" / "plugins" / "marketplace.json").write_text(
        dump_json(native_marketplace(snapshot))
    )
    (target / ".claude-plugin" / "marketplace.json").write_text(
        dump_json(claude_marketplace(snapshot))
    )
    index_path = RELEASES_ROOT / "index.json"
    index = load_json(index_path) if index_path.exists() else {"schemaVersion": 1, "releases": []}
    if not isinstance(index, dict) or not isinstance(index.get("releases"), list):
        raise RuntimeError("releases/index.json is invalid")
    index["releases"].append(
        {
            "release": snapshot["release"],
            "status": snapshot["status"],
            "createdAt": snapshot["createdAt"],
            "path": f"./{snapshot['release']}/release.json",
        }
    )
    index_path.write_text(dump_json(index))
    return target


def check_release(release_id: str, verify_checkouts: bool, require_live: bool) -> list[str]:
    errors: list[str] = []
    target = release_dir(release_id)
    try:
        snapshot = load_json(target / "release.json")
    except ValueError as exc:
        return [str(exc)]
    if not isinstance(snapshot, dict):
        return ["release.json must be an object"]
    if snapshot.get("release") != release_id:
        errors.append("release ID does not match directory name")
    rows = snapshot.get("plugins")
    if not isinstance(rows, list):
        return errors + ["release.plugins must be an array"]
    names = [row.get("name") for row in rows if isinstance(row, dict)]
    if len(names) != len(set(names)):
        errors.append("release plugin names must be unique")
    for row in rows:
        if not isinstance(row, dict):
            errors.append("release plugin entry must be an object")
            continue
        if not SHA.match(str(row.get("commit", ""))):
            errors.append(f"invalid commit pin: {row.get('name')}")
    try:
        actual_native = load_json(target / ".agents" / "plugins" / "marketplace.json")
        errors.extend(validate_native_marketplace(snapshot, actual_native))
        actual_claude = load_json(target / ".claude-plugin" / "marketplace.json")
        errors.extend(validate_claude_marketplace(snapshot, actual_claude))
    except (KeyError, RuntimeError, ValueError) as exc:
        errors.append(str(exc))

    if verify_checkouts:
        row_by_name = {row["name"]: row for row in rows if isinstance(row, dict)}
        for plugin_name, repo_name in PLUGINS:
            repo = LAB_ROOT / repo_name
            if not repo.is_dir():
                errors.append(f"missing sibling checkout: {repo_name}")
                continue
            row = row_by_name.get(plugin_name, {})
            try:
                manifest = manifest_at(repo, str(row.get("commit", "")))
            except (RuntimeError, json.JSONDecodeError) as exc:
                errors.append(str(exc))
                continue
            if manifest.get("version") != row.get("version"):
                errors.append(f"version/commit mismatch: {plugin_name}")

    if require_live:
        try:
            plan = load_json(PLAN_PATH)
        except ValueError as exc:
            errors.append(str(exc))
            plan = {}
        evidence = snapshot.get("connectorEvidence", [])
        requirements = snapshot.get("requiredConnectorProfiles", [])
        if not isinstance(evidence, list) or not isinstance(requirements, list):
            errors.append("connector evidence and requirements must be arrays")
        else:
            reports: list[dict[str, object]] = []
            for relative in evidence:
                try:
                    report = load_json(target / str(relative))
                except ValueError as exc:
                    errors.append(str(exc))
                    continue
                if isinstance(report, dict):
                    reports.append(report)
            for requirement in requirements:
                if not isinstance(requirement, dict):
                    errors.append("invalid requiredConnectorProfiles entry")
                    continue
                host = requirement.get("host")
                profile = requirement.get("profile")
                matching = [report for report in reports if report.get("host") == host]
                if not matching:
                    errors.append(f"missing live connector report: host={host} profile={profile}")
                    continue
                candidate_errors = [
                    validate_report(
                        plan if isinstance(plan, dict) else {},
                        report,
                        expected_release=release_id,
                        required_profile=str(profile),
                    )
                    for report in matching
                ]
                if all(candidate_errors):
                    errors.append(
                        f"no valid live connector report for host={host} profile={profile}"
                    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    snapshot_parser = sub.add_parser("snapshot")
    snapshot_parser.add_argument("--release", required=True)
    snapshot_parser.add_argument("--revision", default="origin/main")
    snapshot_parser.add_argument("--allow-dirty", action="store_true")
    snapshot_parser.add_argument("--write", action="store_true")
    check_parser = sub.add_parser("check")
    check_parser.add_argument("--release")
    check_parser.add_argument("--all", action="store_true")
    check_parser.add_argument("--verify-checkouts", action="store_true")
    check_parser.add_argument("--require-live", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "snapshot":
            snapshot = build_snapshot(args.release, args.revision, args.allow_dirty)
            if args.write:
                target = write_snapshot(snapshot)
                print(f"Wrote release candidate: {target}")
            else:
                print(dump_json(snapshot), end="")
            return 0
        index = load_json(RELEASES_ROOT / "index.json")
        if not isinstance(index, dict):
            raise RuntimeError("releases/index.json must be an object")
        if args.all:
            release_ids = [row["release"] for row in index.get("releases", [])]
        elif args.release:
            release_ids = [args.release]
        else:
            raise RuntimeError("check requires --release or --all")
        errors: list[str] = []
        for release_id in release_ids:
            errors.extend(
                f"{release_id}: {error}"
                for error in check_release(
                    release_id, args.verify_checkouts, args.require_live
                )
            )
        if errors:
            print("Release validation failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
        print(f"Release validation passed: {', '.join(release_ids)}")
        return 0
    except (KeyError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
