#!/usr/bin/env python3
"""Fixture-only validation for the Nucleus OpenAI marketplace and adapters."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from catalog import PLUGIN_NAMES, PLUGIN_REPOSITORIES


NUCLEUS_ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = NUCLEUS_ROOT.parent
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
ACTIVE_SOURCE_DIRS = ("commands", "skills", "agents", "references", "claude-code")
ACTIVE_ROOT_DOCS = ("README.md", "SECURITY.md", "CLAUDE.md", "AGENTS.md")
LEGACY_COMPAT_MARKER = "LEGACY_COMPAT"
ARCHITECTURE_GUARDS = (
    (
        "hard-coded pre-scope identity/voice path",
        re.compile(r"~/Documents/Claude/(?:identity|voice)\.md"),
    ),
    (
        "hard-coded pre-resolver memory path",
        re.compile(r"~/Documents/Claude/memory/"),
    ),
    (
        "retired plugin state path outside an annotated compatibility branch",
        re.compile(
            r"<config-root>/plugins/(?:lead-engine|referral-engine|weekly-outreach|"
            r"client-status|project-setup)(?:[./`])"
        ),
    ),
    (
        "retired plugin treated as a current installed dependency",
        re.compile(
            r"(?i)(?:if|when) (?:the )?(?:lead-engine|referral-engine|weekly-outreach|"
            r"client-status|project-setup)(?: plugin)? is (?:still )?installed"
        ),
    ),
)


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON {path.relative_to(LAB_ROOT)}: {exc}")
        return {}


def frontmatter(path: Path, errors: list[str]) -> dict[str, str]:
    text = path.read_text()
    require(text.startswith("---\n"), f"missing frontmatter: {path.relative_to(LAB_ROOT)}", errors)
    try:
        raw = text.split("---\n", 2)[1]
    except IndexError:
        errors.append(f"unterminated frontmatter: {path.relative_to(LAB_ROOT)}")
        return {}
    fields: dict[str, str] = {}
    for line in raw.splitlines():
        match = re.match(r"^([a-zA-Z0-9_-]+):\s*(.*)$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip()
    return fields


def check_manifest(repo: Path, expected_name: str, errors: list[str]) -> str:
    manifest = load_json(repo / ".codex-plugin" / "plugin.json", errors)
    require(manifest.get("name") == expected_name, f"manifest name mismatch: {repo.name}", errors)
    version = str(manifest.get("version", ""))
    require(bool(SEMVER.match(version)), f"invalid semver in {repo.name}: {version}", errors)
    interface = manifest.get("interface", {})
    for field in ("displayName", "shortDescription", "longDescription", "developerName", "category", "capabilities", "defaultPrompt"):
        require(bool(interface.get(field)), f"missing interface.{field}: {repo.name}", errors)
    prompts = interface.get("defaultPrompt", [])
    require(isinstance(prompts, list) and len(prompts) <= 3, f"too many default prompts: {repo.name}", errors)
    for prompt in prompts if isinstance(prompts, list) else []:
        require(len(prompt) <= 128, f"default prompt over 128 chars: {repo.name}", errors)
    return version


def check_skills(repo: Path, errors: list[str]) -> None:
    skills = {path.parent.name: path for path in (repo / "skills").glob("*/SKILL.md")}
    require(bool(skills), f"no skills found: {repo.name}", errors)
    for folder, path in skills.items():
        fields = frontmatter(path, errors)
        require(fields.get("name") == folder, f"skill name/folder mismatch: {repo.name}/{folder}", errors)
        require(bool(fields.get("description")), f"missing skill description: {repo.name}/{folder}", errors)
        text = path.read_text()
        if repo.name == "cortex":
            require(
                "commands/" in text or "canonical" in text or "scripts/cortex_cli.py" in text,
                f"Cortex skill is not a canonical wrapper: {repo.name}/{folder}",
                errors,
            )
        else:
            require(
                "openai-portability.md" in text,
                f"skill missing OpenAI binding: {repo.name}/{folder}",
                errors,
            )
    command_dir = repo / "commands"
    if command_dir.is_dir():
        for command in command_dir.glob("*.md"):
            require(command.stem in skills, f"command has no GPT skill: {repo.name}/{command.stem}", errors)


def check_agents(repo: Path, errors: list[str]) -> None:
    source = repo / "agents"
    if not source.is_dir():
        return
    for role in source.glob("*.md"):
        binding = repo / ".codex" / "agents" / f"{role.stem}.toml"
        require(binding.exists(), f"agent has no Codex binding: {repo.name}/{role.stem}", errors)
        if binding.exists():
            text = binding.read_text()
            require('sandbox_mode = "read-only"' in text, f"agent is not read-only: {repo.name}/{role.stem}", errors)


def check_active_architecture(repo: Path, errors: list[str]) -> None:
    """Keep retired names and vendor paths behind explicit compatibility branches."""
    paths = [repo / name for name in ACTIVE_ROOT_DOCS if (repo / name).is_file()]
    for directory in ACTIVE_SOURCE_DIRS:
        root = repo / directory
        if not root.is_dir():
            continue
        paths.extend(sorted(root.rglob("*.md")))
    for path in paths:
        lines = path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            context = "\n".join(lines[max(0, index - 1) : index + 2])
            for label, pattern in ARCHITECTURE_GUARDS:
                if pattern.search(line) and LEGACY_COMPAT_MARKER not in context:
                    display_path = (
                        path.relative_to(LAB_ROOT)
                        if path.is_relative_to(LAB_ROOT)
                        else path
                    )
                    errors.append(
                        f"{label}: {display_path}:{index + 1}; "
                        f"migrate it or annotate the compatibility branch with {LEGACY_COMPAT_MARKER}"
                    )


def check_config_root_fixture(errors: list[str]) -> None:
    module_path = LAB_ROOT / "cortex" / "scripts" / "lib" / "config_root.py"
    spec = importlib.util.spec_from_file_location("cortex_config_root_fixture", module_path)
    require(spec is not None and spec.loader is not None, "cannot load Cortex config-root resolver", errors)
    if spec is None or spec.loader is None:
        return
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix="nucleus-openai-") as tmp:
        home = Path(tmp) / "home"
        home.mkdir()
        default = module.resolve_config_root(home=home, environ={})
        require(default.path == home / "Documents" / "Claude", "fixture default config root failed", errors)
        legacy_root = Path(tmp) / "legacy-root"
        legacy = home / "Documents" / ".claude-plugin-config-root"
        legacy.parent.mkdir(parents=True)
        legacy.write_text(f"{legacy_root}\n")
        result = module.resolve_config_root(home=home, environ={})
        require(result.path == legacy_root, "fixture legacy pointer failed", errors)
        vendor_root = Path(tmp) / "vendor-root"
        vendor = home / ".cortex" / "config-root"
        vendor.parent.mkdir(parents=True)
        vendor.write_text(f"{vendor_root}\n")
        result = module.resolve_config_root(home=home, environ={})
        require(result.path == vendor_root, "fixture vendor pointer precedence failed", errors)
        env_root = Path(tmp) / "env-root"
        result = module.resolve_config_root(home=home, environ={"CORTEX_CONFIG_ROOT": str(env_root)})
        require(result.path == env_root, "fixture environment precedence failed", errors)


def main() -> int:
    errors: list[str] = []
    generated = subprocess.run(
        [sys.executable, str(NUCLEUS_ROOT / "scripts" / "generate_openai_adapters.py"), "--check"],
        cwd=NUCLEUS_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    require(generated.returncode == 0, generated.stderr.strip() or "generated adapters are stale", errors)

    native = load_json(NUCLEUS_ROOT / ".agents" / "plugins" / "marketplace.json", errors)
    native_entries = native.get("plugins", [])
    require(len(native_entries) == len(PLUGIN_NAMES), "native marketplace must contain 9 plugins", errors)
    native_names = [entry.get("name") for entry in native_entries]
    require(native_names == list(PLUGIN_NAMES), "native marketplace ordering/names differ", errors)
    for entry in native_entries:
        source = entry.get("source", {})
        require(source.get("source") == "url", f"native source is not url: {entry.get('name')}", errors)
        require(str(source.get("url", "")).startswith("https://github.com/BrightWayAI/"), f"invalid source URL: {entry.get('name')}", errors)
        require(entry.get("policy", {}).get("installation") in {"AVAILABLE", "INSTALLED_BY_DEFAULT"}, f"missing installation policy: {entry.get('name')}", errors)

    connector_plan = load_json(NUCLEUS_ROOT / "connector-tests" / "plan.json", errors)
    connector_ids = [
        row.get("id")
        for row in connector_plan.get("connectors", [])
        if isinstance(row, dict)
    ]
    connector_command = (LAB_ROOT / "ops" / "commands" / "test-connectors.md").read_text()
    for connector_id in connector_ids:
        require(
            f"`{connector_id}`" in connector_command,
            f"ops connector workflow missing plan ID: {connector_id}",
            errors,
        )

    claude = load_json(NUCLEUS_ROOT / ".claude-plugin" / "marketplace.json", errors)
    claude_versions = {entry.get("name"): str(entry.get("version")) for entry in claude.get("plugins", [])}
    for plugin_name, repo_name, claude_name in PLUGIN_REPOSITORIES:
        repo = LAB_ROOT / repo_name
        require(repo.is_dir(), f"missing repository: {repo_name}", errors)
        if not repo.is_dir():
            continue
        version = check_manifest(repo, plugin_name, errors)
        require(claude_versions.get(claude_name) == version, f"catalog version mismatch: {repo_name}", errors)
        check_skills(repo, errors)
        check_agents(repo, errors)
        check_active_architecture(repo, errors)
        require((repo / "AGENTS.md").exists(), f"missing AGENTS.md: {repo_name}", errors)
        require((repo / "references" / "openai-portability.md").exists() or repo_name == "cortex", f"missing portability contract: {repo_name}", errors)

    retired = {"nucleus-router", "lead-engine", "project-setup", "client-status", "referral-engine", "writing-style"}
    require(not retired.intersection(native_names), "native marketplace contains retired plugins", errors)
    require(not retired.intersection(claude_versions), "Claude marketplace contains retired plugins", errors)
    require((LAB_ROOT / "ops" / "commands" / "cos.md").exists(), "ops is missing the chief-of-staff entrypoint", errors)
    for command in ("pull-signals", "capture-signal", "pre-call-brief"):
        require((LAB_ROOT / "growth" / "commands" / f"{command}.md").exists(), f"growth is missing absorbed command: {command}", errors)
    for command in ("project-setup", "client-status", "review-deliverable"):
        require((LAB_ROOT / "clients" / "commands" / f"{command}.md").exists(), f"clients is missing absorbed command: {command}", errors)
    check_config_root_fixture(errors)

    releases = subprocess.run(
        [sys.executable, str(NUCLEUS_ROOT / "scripts" / "release_ecosystem.py"), "check", "--all"],
        cwd=NUCLEUS_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    require(releases.returncode == 0, releases.stderr.strip() or "release snapshots are invalid", errors)

    if errors:
        print("Nucleus OpenAI ecosystem check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Nucleus OpenAI ecosystem check passed (9 plugins; fixture-only config-root tests).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
