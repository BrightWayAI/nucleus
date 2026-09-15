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


NUCLEUS_ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = NUCLEUS_ROOT.parent
PLUGIN_NAMES = [
    "nucleus-router",
    "claude-cortex",
    "lead-engine",
    "weekly-alignment",
    "core-ops",
    "news-curator",
    "project-setup",
    "time-tracking",
    "client-status",
    "referral-engine",
    "relationships",
    "writing-style",
    "daily-brief",
]
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


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


def check_manifest(repo: Path, errors: list[str]) -> tuple[str, str]:
    manifest = load_json(repo / ".codex-plugin" / "plugin.json", errors)
    expected_name = "cortex" if repo.name == "claude-cortex" else repo.name
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
    return expected_name, version


def check_skills(repo: Path, errors: list[str]) -> None:
    skills = {path.parent.name: path for path in (repo / "skills").glob("*/SKILL.md")}
    require(bool(skills), f"no skills found: {repo.name}", errors)
    for folder, path in skills.items():
        fields = frontmatter(path, errors)
        require(fields.get("name") == folder, f"skill name/folder mismatch: {repo.name}/{folder}", errors)
        require(bool(fields.get("description")), f"missing skill description: {repo.name}/{folder}", errors)
        text = path.read_text()
        if repo.name == "claude-cortex":
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
        if repo.name == "claude-cortex" and role.stem == "conversation-miner":
            continue
        binding = repo / ".codex" / "agents" / f"{role.stem}.toml"
        require(binding.exists(), f"agent has no Codex binding: {repo.name}/{role.stem}", errors)
        if binding.exists():
            text = binding.read_text()
            require('sandbox_mode = "read-only"' in text, f"agent is not read-only: {repo.name}/{role.stem}", errors)


def check_config_root_fixture(errors: list[str]) -> None:
    module_path = LAB_ROOT / "claude-cortex" / "scripts" / "lib" / "config_root.py"
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
    require(len(native_entries) == 13, "native marketplace must contain 13 plugins", errors)
    native_names = [entry.get("name") for entry in native_entries]
    require(native_names == ["nucleus-router", "cortex", *PLUGIN_NAMES[2:]], "native marketplace ordering/names differ", errors)
    for entry in native_entries:
        source = entry.get("source", {})
        require(source.get("source") == "url", f"native source is not url: {entry.get('name')}", errors)
        require(str(source.get("url", "")).startswith("https://github.com/BrightWayAI/"), f"invalid source URL: {entry.get('name')}", errors)
        require(entry.get("policy", {}).get("installation") in {"AVAILABLE", "INSTALLED_BY_DEFAULT"}, f"missing installation policy: {entry.get('name')}", errors)

    claude = load_json(NUCLEUS_ROOT / ".claude-plugin" / "marketplace.json", errors)
    claude_versions = {entry.get("name"): str(entry.get("version")) for entry in claude.get("plugins", [])}
    for repo_name in PLUGIN_NAMES:
        repo = LAB_ROOT / repo_name
        require(repo.is_dir(), f"missing repository: {repo_name}", errors)
        if not repo.is_dir():
            continue
        manifest_name, version = check_manifest(repo, errors)
        catalog_name = "claude-cortex" if manifest_name == "cortex" else manifest_name
        require(claude_versions.get(catalog_name) == version, f"catalog version mismatch: {repo_name}", errors)
        check_skills(repo, errors)
        check_agents(repo, errors)
        require((repo / "AGENTS.md").exists(), f"missing AGENTS.md: {repo_name}", errors)
        require((repo / "references" / "openai-portability.md").exists() or repo_name == "claude-cortex", f"missing portability contract: {repo_name}", errors)

    lead_skill = (LAB_ROOT / "lead-engine" / "skills" / "lead-engine" / "SKILL.md").read_text()
    require("`references/pipeline.md`" not in lead_skill, "lead-engine still writes plugin-relative pipeline", errors)
    router = (LAB_ROOT / "nucleus-router" / "skills" / "route" / "SKILL.md").read_text()
    require("| bizdev-outreach |" not in router and "| weekly-outreach |" not in router, "router still routes to retired plugins", errors)
    check_config_root_fixture(errors)

    if errors:
        print("Nucleus OpenAI ecosystem check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Nucleus OpenAI ecosystem check passed (13 plugins; fixture-only config-root tests).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
