#!/usr/bin/env python3
"""Generate and validate the OpenAI adapter surface for the Nucleus catalog.

This script only writes repository files. It never resolves a user's config root,
reads user data, or touches Cortex memory. Run with --check in CI and --write when
updating the catalog.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from catalog import PLUGIN_REPOSITORIES


NUCLEUS_ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = NUCLEUS_ROOT.parent

PLUGINS = {
    "cortex": {
        "display": "Cortex",
        "short": "One shared second brain across AI hosts",
        "long": "Recall, search, and explicitly commit to one user-owned Cortex memory store from Claude, ChatGPT, or Codex.",
        "category": "Productivity",
        "capabilities": ["Read", "Write"],
        "prompts": ["Set up my Cortex memory.", "Recall what we know about this topic.", "Show what this conversation would add before saving."],
        "degraded": "Direct local-memory access requires a filesystem-capable host and permission to the resolved config root. Cloud sessions require the approved bounded bridge; never redirect memory to another store silently.",
    },
    "alignment": {
        "display": "Team Alignment",
        "short": "Find cross-team overlaps, conflicts, and decision risks",
        "long": "Scan configured Slack sources for cross-team alignment signals and produce daily pulses, weekly reports, and risk updates.",
        "category": "Teamwork",
        "capabilities": ["Read", "Write"],
        "prompts": ["Scan Slack for alignment risks.", "Create this week's alignment report.", "Update our monitored risks."],
        "degraded": "A readable Slack app or MCP connector is required for scans. Without one, explain the dependency and stop; never invent channel activity. Previously saved local history may still be reviewed.",
        "skill_names": {"daily-pulse": "daily-pulse", "report": "report", "scan": "scan", "setup": "setup", "update-risks": "update-risks"},
    },
    "ops": {
        "display": "Chief of Staff",
        "short": "Route work and run stack operations",
        "long": "Use a natural-language chief-of-staff front door, inspect Nucleus health, record agent metrics, and register schedules when the host supports them. Delegates CRM pipeline analysis and forecasting to the growth plugin when installed.",
        "category": "Business",
        "capabilities": ["Read", "Write", "Interactive"],
        "prompts": ["What can Nucleus do?", "Diagnose my Nucleus setup.", "Register my Nucleus schedules."],
        "degraded": "CRM, artifacts, and scheduling are independent capabilities. Use available inputs, name missing specialist plugins, and provide schedule definitions without claiming registration when no scheduler exists.",
    },
    "research": {
        "display": "Research",
        "short": "Research and stage a cited weekly news roundup",
        "long": "Find recent stories, rank them for a configured audience, and stage candidates with traceable sources for drafting elsewhere.",
        "category": "Research",
        "capabilities": ["Read", "Interactive"],
        "prompts": ["Research this week's top stories.", "Stage this week's roundup candidates.", "Configure my roundup audience."],
        "degraded": "Web search is required for fresh research. Mail/newsletter connectors are optional. If delegation is unavailable, run the curator stage inline and preserve source citations.",
    },
    "clients": {
        "display": "Client Success",
        "short": "Start, support, document, and QA client engagements",
        "long": "Create engagement plans and portable workspace prompts, draft weekly client-status updates, run structured deliverable QA, and turn approved proposals into reviewed Statements of Work.",
        "category": "Productivity",
        "capabilities": ["Read", "Write", "Interactive"],
        "prompts": ["Set up a client engagement.", "Draft this week's client status update.", "Turn this proposal into a reviewed Statement of Work."],
        "degraded": "When Drive or project-creation APIs are absent, return a folder blueprint and host-neutral workspace prompt. Use available evidence for status and QA, list skipped sources, and keep outbound updates as drafts. For SOW generation, use the host's document capability when available; otherwise use the bundled PEP 723 Python scripts through `uv run`. Never claim visual review when no renderer is available.",
        "portable_notes": """### Generated documents on OpenAI hosts

Treat a canonical `AskUserQuestion` step as one grouped question using the host's
available elicitation UI or a single chat message. Treat `SendUserFile` as the host's
generated-file attachment when available; in Codex CLI, save the file inside the
workspace and report its absolute path plus the checks performed. For `.docx` visual
QA, use the installed document-artifact renderer when available. A raw XML/text check
does not replace rendered-page inspection.
""",
    },
    "admin": {
        "display": "Admin",
        "short": "Classify calendar time and prepare reviewable invoices",
        "long": "Turn calendar events into a local, reviewable time log and generate invoice drafts from configured client billing rules.",
        "category": "Business",
        "capabilities": ["Read", "Write"],
        "prompts": ["Track yesterday's billable time.", "Generate this month's invoice drafts.", "Configure my billing rules."],
        "degraded": "A calendar connector is optional: accept pasted events when absent. Generate Markdown or structured invoice data if document tooling is unavailable. Never send invoices automatically.",
    },
    "growth": {
        "display": "Growth Engine",
        "short": "Prioritize relationship actions and draft useful touchpoints",
        "long": "Build a daily relationship cockpit, research contacts, act on buying signals and referral opportunities, rebalance a network, rank and forecast pipeline, and create context-aware touchpoint drafts.",
        "category": "Sales",
        "capabilities": ["Read", "Write", "Interactive"],
        "prompts": ["Build today's relationship brief.", "Draft a touchpoint for this person.", "Analyze my pipeline."],
        "degraded": "Cortex, CRM, mail, calendar, Apollo, and research connectors enrich ranking but are optional. Run read-only role work inline when agents are unavailable, name skipped sources, and keep all outbound content as drafts.",
        "skill_names": {"setup": "setup"},
    },
    "comms": {
        "display": "Comms Desk",
        "short": "Draft in your voice and learn from approved edits",
        "long": "Create voice-matched drafts, assemble the weekly roundup post from staged research candidates, compare drafts with final edits, and propose durable style-rule updates only after repeated evidence.",
        "category": "Writing",
        "capabilities": ["Read", "Write"],
        "prompts": ["Write this in my voice.", "Draft my roundup post.", "Learn from these edits."],
        "degraded": "Mail and publishing connectors are optional. Accept pasted samples and return copy-ready text when absent. Never send or publish automatically; style-file changes require user approval.",
    },
    "briefing": {
        "display": "Today's Brief",
        "short": "Build and process a daily operating brief",
        "long": "Combine calendar, tasks, outreach, inbox, CRM, and Cortex context into a daily brief, then process user-approved annotations and plan tomorrow.",
        "category": "Productivity",
        "capabilities": ["Read", "Write", "Interactive"],
        "prompts": ["Build today's brief.", "Process these brief annotations.", "Plan my next business day."],
        "degraded": "Cowork's interactive artifact is not portable. In ChatGPT and Codex, write a Markdown snapshot and preserve user-supplied actions in the canonical local v0.7.0 state file so cortex /listen can mine the same round-trip. Missing connectors are listed and skipped; no mail, CRM, or calendar mutation occurs without confirmation.",
        "portable_notes": """### Chat-native brief state on OpenAI hosts

When no interactive artifact is available, render the Markdown brief with the same
stable task, outreach, and event ids used by the canonical artifact. If the user
marks an item done, delegates it, snoozes it, changes its priority, adds an
annotation, or supplies today's reflection in chat, merge only those explicit
choices into `<config-root>/briefs/<YYYY-MM-DD>.state.json` using the canonical
v0.7.0 shape from `commands/brief.md`. Preserve existing keys and update
`last_interaction_at`; never infer a click or disposition from silence.

This local state file is the OpenAI-host equivalent of the artifact's state mirror.
`/process-brief` may act on it during the day, and cortex `/listen` mines it
overnight before `/morning` reviews durable memory proposals. If no explicit state
was recorded, `/listen` may still run its evidence-based inference pass against the
Markdown twin and available archive sources.
""",
    },
}

ALIASES = {
    "ops": ["setup-core"],
    "research": ["setup-news"],
    "clients": ["setup-projects", "setup-status"],
    "admin": ["setup-time"],
    "growth": ["setup-relationships"],
    "comms": ["setup-voice", "setup-style", "style"],
    "briefing": ["setup-brief"],
}

DISABLED_ALIASES = {
    ("ops", "setup-core"),
    ("research", "setup-news"),
    ("clients", "setup-projects"),
    ("clients", "setup-status"),
    ("admin", "setup-time"),
    ("growth", "setup-relationships"),
    ("comms", "setup-voice"),
    ("comms", "setup-style"),
    ("briefing", "setup-brief"),
}

AGENTS = {
    "alignment": ["alignment-scanner"],
    "ops": ["chief-of-staff"],
    "research": ["news-curator"],
    "comms": ["post-assembler"],
    "growth": ["relationships-director", "pipeline-analyst", "pipeline-forecast"],
}

PREAMBLE_START = "<!-- OPENAI-ADAPTER:START -->"
PREAMBLE_END = "<!-- OPENAI-ADAPTER:END -->"
PREAMBLE = f"""{PREAMBLE_START}
## OpenAI host binding

Before acting, read `../../references/openai-portability.md`. That file translates
host-specific tools, agents, artifacts, scheduling, connectors, and config-root
access for ChatGPT and Codex. It overrides concrete Claude/Cowork tool names only;
the workflow, safety gates, and output contract in this skill remain canonical.
{PREAMBLE_END}
"""
README_START = "<!-- OPENAI-SUPPORT:START -->"
README_END = "<!-- OPENAI-SUPPORT:END -->"


def dump_json(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def write_or_check(path: Path, content: str, write: bool, errors: list[str]) -> None:
    current = path.read_text() if path.exists() else None
    if current == content:
        return
    if write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    else:
        errors.append(f"stale or missing: {path.relative_to(LAB_ROOT)}")


def command_description(path: Path, command: str) -> str:
    if not path.exists():
        return f"Run the {command} workflow. Use when the user asks for this capability or invokes /{command}."
    text = path.read_text()
    match = re.search(r"^description:\s*(.*)$", text, re.MULTILINE)
    if not match:
        return f"Run the {command} workflow. Use when the user asks for this capability or invokes /{command}."
    value = match.group(1).strip()
    if value in {">", "|", ">-", "|-"}:
        lines = []
        for line in text[match.end():].splitlines()[1:]:
            if line.startswith((" ", "\t")):
                lines.append(line.strip())
            else:
                break
        value = " ".join(lines)
    value = value.strip('"\'')
    return value[:900] if value else f"Run the {command} workflow."


def manifest(name: str, repo_name: str, data: dict[str, object]) -> dict[str, object]:
    return {
        "name": name,
        "version": data["version"],
        "description": data["long"],
        "author": {"name": "BrightWay AI", "url": "https://brightwayai.com"},
        "license": "MIT",
        "homepage": f"https://github.com/BrightWayAI/{repo_name}",
        "repository": f"https://github.com/BrightWayAI/{repo_name}",
        "keywords": ["nucleus", "chatgpt", "codex"],
        "skills": "./skills/",
        "interface": {
            "displayName": data["display"],
            "shortDescription": data["short"],
            "longDescription": data["long"],
            "developerName": "BrightWay AI",
            "category": data["category"],
            "capabilities": data["capabilities"],
            "websiteURL": f"https://github.com/BrightWayAI/{repo_name}",
            "defaultPrompt": data["prompts"],
        },
    }


def agents_md(name: str, data: dict[str, object]) -> str:
    agent_line = ""
    if name in AGENTS:
        agent_line = "\nRead-only Codex role bindings live in `.codex/agents/`. If role delegation is unavailable, execute the same source role inline and preserve its read-only boundary.\n"
    return f"""# {data['display']} — OpenAI host entrypoint

This repository supports Claude Code/Cowork, ChatGPT desktop Local Work, and Codex
from one canonical workflow source.

Read in this order:

1. `references/openai-portability.md` for host capability and degradation rules.
2. The matching `skills/<name>/SKILL.md` for workflow instructions.
3. Any `commands/<name>.md` and references named by that skill.

Treat `commands/` and authored `skills/` as canonical. OpenAI alias skills are thin
entrypoints and must not fork workflow behavior. Treat the installed plugin directory
as read-only at runtime. User state belongs under the shared `<config-root>` resolved
by the precedence chain in the portability reference.{agent_line}
Never fabricate connector data. Keep drafts as drafts, and confirm any external write,
send, schedule registration, or destructive action at the point of action.
"""


def portability_md(name: str, data: dict[str, object]) -> str:
    portable_notes = str(data.get("portable_notes", "")).strip()
    portable_notes_block = f"\n\n{portable_notes}" if portable_notes else ""
    return f"""# OpenAI portability contract — {data['display']}

This file binds the plugin's canonical Claude-oriented examples to ChatGPT and Codex.
It changes tool names and unavailable-host behavior, not the workflow's business logic
or safety gates.

## Shared config root

Resolve `<config-root>` with the same chain used by Cortex, in this exact order:

1. `CORTEX_CONFIG_ROOT` environment variable, when set to a non-empty path.
2. First non-empty line of `~/.cortex/config-root`.
3. First non-empty line of legacy `~/Documents/.claude-plugin-config-root`.
4. Default `~/Documents/Claude`.

An explicit path supplied for the current workflow may be used for that invocation,
but do not create a GPT-specific pointer. Expand `~`, use an absolute path, and ask for
filesystem permission when the resolved root is outside the host's writable roots.
If a new OpenAI-host user chooses a persistent root, configure it through Cortex or
write `~/.cortex/config-root` only after confirmation. Never overwrite a pointer that
targets a different root without a second explicit confirmation, and do not create or
update the legacy Claude pointer from an OpenAI host.
Identity and voice remain shared files at `<config-root>/memory/me/identity.md` and
`<config-root>/memory/me/voice.md`. Plugin state belongs under `<config-root>`—normally
`<config-root>/plugins/`—never inside the installed plugin directory.

## Invocation

- ChatGPT desktop: enable the plugin in a chat, then ask naturally or use `@{data['display']} <request>`.
- Codex: ask naturally or invoke the namespaced Agent Skill shown by the client.
- Claude slash commands remain aliases in prose. `/example` means the matching skill
  workflow; it does not require an OpenAI slash-command feature.

## Capability translation

| Canonical intent | ChatGPT / Codex behavior |
|---|---|
| Read or write local files | Use Local Work or sandbox filesystem access scoped to `<config-root>`. Request the smallest additional writable root needed. |
| Read a connector | Use an installed ChatGPT app or MCP server. Check availability first; never infer that a named Claude/Cowork connector exists. |
| Write through a connector | Preview the exact mutation and obtain confirmation immediately before it. Keep draft-only steps as drafts. |
| Web research | Use current web search with citations. If unavailable, ask for sources or stop the fresh-research portion. |
| Delegate to an agent | Use the matching read-only `.codex/agents` role when available; otherwise follow the role inline. |
| Create a Cowork artifact | Produce the same information as Markdown or a supported document artifact. Do not claim Cowork interactivity or localStorage state. |
| Register a schedule | Use a host scheduler only when exposed and after confirmation. Otherwise return a schedule definition for manual setup. |
| Select a Claude model tier | Preserve the intent (fast/low-cost vs. deep synthesis) using the host's available model; ignore Claude model names. |

ChatGPT desktop Local Work and Codex can share the exact same local files as Claude
when they resolve the same `<config-root>`. ChatGPT web/cloud sessions cannot access a
private local folder merely because this plugin is installed. They need an approved
remote app/MCP bridge; otherwise local-memory operations are unavailable, not silently
redirected to another store.

## Plugin-specific degradation

{data['degraded']}{portable_notes_block}

Always report unavailable or skipped capabilities in the result. A degraded run must
remain useful where possible, but it must never imply that missing data was read or an
external action happened.
"""


def wrapper_md(repo: Path, name: str, command: str) -> str:
    desc = command_description(repo / "commands" / f"{command}.md", command)
    disabled = "disable-model-invocation: true\n" if (name, command) in DISABLED_ALIASES else ""
    yaml_description = json.dumps(desc, ensure_ascii=False)
    return f"""---
{disabled}name: {command}
description: {yaml_description}
---

# {command}

Read `../../references/openai-portability.md`, then read
`../../commands/{command}.md` completely and follow it as the canonical workflow.
Treat `/{command}`, `${command}`, natural-language activation, and the ChatGPT plugin
mention as equivalent entrypoints. Ignore Claude-only tool allowlists and model names;
apply the capability translation and degradation rules from the portability contract.

Do not duplicate or reinterpret the command here. Preserve its confirmation gates,
draft-only boundaries, file locations, and output contract.
"""


def agent_toml(name: str, role: str) -> str:
    descriptions = {
        "alignment-scanner": "Read Slack and synthesize cross-team alignment evidence in scan, pulse, or report mode.",
        "chief-of-staff": "Return a structured route plan for Nucleus work; the parent validates and executes it.",
        "pipeline-analyst": "Read and rank CRM pipeline evidence without changing CRM or local state.",
        "pipeline-forecast": "Build an evidence-based pipeline forecast without changing source systems.",
        "news-curator": "Research and rank recent news candidates with citations.",
        "post-assembler": "Assemble approved news candidates into a voice-matched draft.",
        "relationships-director": "Rank relationship actions or research one contact/company in the caller-selected mode.",
    }
    mode_rule = {
        "alignment-scanner": 'The caller must pass mode "scan", "pulse", or "report"; follow only that mode.',
        "relationships-director": 'The caller must pass mode "rank" or "research"; follow only that mode.',
    }.get(role, "")
    mode_line = f"{mode_rule}\n" if mode_rule else ""
    instruction_tail = (
        "evidence. Return exactly one route_plan to the parent. Do not invoke target skills or\n"
        "other agents, write local state, mutate connectors, send messages, or schedule work.\n"
        "If delegation is unavailable, the parent must follow the same planner role inline\n"
        "with this read-only boundary."
        if role == "chief-of-staff"
        else "evidence. Return findings to the parent. Do not write local state, mutate connectors,\n"
        "send messages, or schedule work. If delegation is unavailable, the parent must follow\n"
        "the same role inline with this read-only boundary."
    )
    return f'''name = "{role}"
description = "{descriptions[role]}"
sandbox_mode = "read-only"
developer_instructions = """
Read AGENTS.md, references/openai-portability.md, and agents/{role}.md completely.
{mode_line}Treat Claude model/tool metadata as source-host examples. Use only connector and web
capabilities actually available, explicitly list skipped sources, and never fabricate
{instruction_tail}
"""
'''


def update_skill(path: Path, replacement_name: str | None, write: bool, errors: list[str]) -> None:
    text = path.read_text()
    changed = text
    if replacement_name:
        changed = re.sub(r"^name:\s*.*$", f"name: {replacement_name}", changed, count=1, flags=re.MULTILINE)
    if PREAMBLE_START not in changed:
        end = changed.find("\n---", 4)
        if end == -1:
            errors.append(f"invalid frontmatter: {path.relative_to(LAB_ROOT)}")
            return
        insert_at = end + 4
        changed = changed[:insert_at] + "\n\n" + PREAMBLE + changed[insert_at:]
    if changed != text:
        if write:
            path.write_text(changed)
        else:
            errors.append(f"stale OpenAI preamble/name: {path.relative_to(LAB_ROOT)}")


def source_version(repo: Path) -> str:
    value = json.loads((repo / ".claude-plugin" / "plugin.json").read_text())
    version = value.get("version")
    if not isinstance(version, str) or not version:
        raise ValueError(f"missing source plugin version: {repo}")
    return version


def update_cortex_adapter(
    repo: Path, version: str, write: bool, errors: list[str]
) -> None:
    portable_path = repo / "plugin.json"
    portable = json.loads(portable_path.read_text())
    portable["version"] = version
    write_or_check(portable_path, dump_json(portable), write, errors)

    source = repo / "adapters" / "chatgpt_work" / "codex-plugin.json"
    value = json.loads(source.read_text())
    value["version"] = version
    content = dump_json(value)
    write_or_check(source, content, write, errors)
    write_or_check(repo / ".codex-plugin" / "plugin.json", content, write, errors)

    mode = "--write" if write else "--check"
    generated = subprocess.run(
        [sys.executable, str(repo / "scripts" / "generate_codex_skills.py"), mode],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    if generated.returncode:
        detail = generated.stderr.strip() or generated.stdout.strip()
        errors.append(f"Cortex Codex skill generation failed: {detail}")


def remove_stale_agent_bindings(
    repo: Path, expected: set[str], write: bool, errors: list[str]
) -> None:
    binding_dir = repo / ".codex" / "agents"
    for binding in binding_dir.glob("*.toml"):
        if binding.stem in expected:
            continue
        if write:
            binding.unlink()
        else:
            errors.append(f"stale Codex agent binding: {binding.relative_to(LAB_ROOT)}")


def marketplace(native: bool, resolved: dict[str, dict[str, object]]) -> dict[str, object]:
    entries = []
    for name, repo_name, claude_name in PLUGIN_REPOSITORIES:
        data = resolved[name]
        if native:
            source = {"source": "url", "url": f"https://github.com/BrightWayAI/{repo_name}.git"}
            category = data["category"]
            entries.append({
                "name": name,
                "source": source,
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": category,
            })
        else:
            entries.append({
                "name": claude_name,
                "version": data["version"],
                "source": {"source": "github", "repo": f"BrightWayAI/{repo_name}"},
                "description": data["long"],
                "author": {"name": "BrightWay AI"},
            })
    if native:
        return {"name": "nucleus", "interface": {"displayName": "Nucleus"}, "plugins": entries}
    return {
        "name": "nucleus",
        "description": "Nucleus — one operating system of portable AI workflows and shared memory for Claude, ChatGPT, and Codex.",
        "owner": {"name": "BrightWay AI"},
        "plugins": entries,
    }


def changelog_entry(version: str) -> str:
    return f"""## [{version}] — OpenAI host adapter (2026-09-14)

### Added
- Native Codex/ChatGPT plugin manifest, durable `AGENTS.md` entrypoint, and an explicit OpenAI capability/degradation contract.
- GPT-discoverable skill aliases for canonical command workflows and read-only Codex role bindings where this plugin ships agents.
- Shared config-root resolution compatible with Cortex and Claude; all GPT tests use repository fixtures or temporary directories only.

"""


def update_changelog(repo: Path, version: str, write: bool, errors: list[str]) -> None:
    path = repo / "CHANGELOG.md"
    text = path.read_text()
    marker = re.compile(rf"^## \[{re.escape(version)}\](?:\s|$)", re.MULTILINE)
    if marker.search(text):
        return
    lines = text.splitlines(keepends=True)
    insert = 2
    while insert < len(lines) and (not lines[insert].strip() or not lines[insert].startswith("## ")):
        insert += 1
    changed = "".join(lines[:insert]) + changelog_entry(version) + "".join(lines[insert:])
    if write:
        path.write_text(changed)
    else:
        errors.append(f"missing changelog entry: {path.relative_to(LAB_ROOT)}")


def update_readme(repo: Path, data: dict[str, object], write: bool, errors: list[str]) -> None:
    path = repo / "README.md"
    text = path.read_text()
    section = f"""{README_START}
## ChatGPT and Codex

{data['display']} ships as a native OpenAI plugin as well as a Claude plugin. In
ChatGPT desktop Local Work, enable **{data['display']}** and ask naturally or mention
`@{data['display']}`. In Codex, use natural language or the namespaced skills exposed
by the plugin. Claude slash-command names in this README remain workflow aliases.

All hosts resolve the same `<config-root>` used by Cortex, so Claude, ChatGPT desktop,
and Codex can share identity, voice, memory, and per-plugin settings without copying
them. The installed plugin directory is read-only at runtime. See
[`references/openai-portability.md`](references/openai-portability.md) for capability
mapping, connector checks, permissions, and honest degraded behavior.

Import the full catalog from
[`BrightWayAI/nucleus`](https://github.com/BrightWayAI/nucleus); Nucleus is the master
marketplace, while each plugin remains independently installable.
{README_END}
"""
    if README_START in text:
        changed = re.sub(
            re.escape(README_START) + r".*?" + re.escape(README_END),
            section.strip(),
            text,
            flags=re.DOTALL,
        )
    else:
        license_match = re.search(r"^## License\s*$", text, re.MULTILINE)
        insert_at = license_match.start() if license_match else len(text)
        prefix = text[:insert_at].rstrip()
        suffix = text[insert_at:].lstrip()
        if suffix:
            changed = prefix + "\n\n" + section.strip() + "\n\n" + suffix
        else:
            changed = prefix + "\n\n" + section.strip() + "\n"
    if changed != text:
        if write:
            path.write_text(changed)
        else:
            errors.append(f"missing or stale OpenAI README section: {path.relative_to(LAB_ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []
    expected_names = {name for name, _, _ in PLUGIN_REPOSITORIES}
    if set(PLUGINS) != expected_names:
        missing = sorted(expected_names - set(PLUGINS))
        extra = sorted(set(PLUGINS) - expected_names)
        print(f"ERROR: adapter metadata differs from catalog (missing={missing}, extra={extra})", file=sys.stderr)
        return 1

    resolved: dict[str, dict[str, object]] = {}
    for name, repo_name, _ in PLUGIN_REPOSITORIES:
        repo = LAB_ROOT / repo_name
        if not repo.is_dir():
            errors.append(f"missing sibling repository: {repo}")
            continue
        data = dict(PLUGINS[name])
        try:
            data["version"] = source_version(repo)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
            continue
        resolved[name] = data

        if name == "cortex":
            update_cortex_adapter(repo, str(data["version"]), args.write, errors)
            continue

        write_or_check(
            repo / ".codex-plugin" / "plugin.json",
            dump_json(manifest(name, repo_name, data)),
            args.write,
            errors,
        )
        write_or_check(repo / "AGENTS.md", agents_md(name, data), args.write, errors)
        write_or_check(repo / "references" / "openai-portability.md", portability_md(name, data), args.write, errors)
        aliases = set(ALIASES.get(name, []))
        for skill in sorted((repo / "skills").glob("*/SKILL.md")):
            folder = skill.parent.name
            if folder in aliases:
                continue
            replacement = data.get("skill_names", {}).get(folder) if isinstance(data.get("skill_names"), dict) else None
            update_skill(skill, replacement, args.write, errors)
        for command in ALIASES.get(name, []):
            write_or_check(repo / "skills" / command / "SKILL.md", wrapper_md(repo, name, command), args.write, errors)
        for role in AGENTS.get(name, []):
            write_or_check(repo / ".codex" / "agents" / f"{role}.toml", agent_toml(name, role), args.write, errors)
        remove_stale_agent_bindings(repo, set(AGENTS.get(name, [])), args.write, errors)
        update_changelog(repo, str(data["version"]), args.write, errors)
        update_readme(repo, data, args.write, errors)

    if set(resolved) == expected_names:
        write_or_check(NUCLEUS_ROOT / ".agents" / "plugins" / "marketplace.json", dump_json(marketplace(True, resolved)), args.write, errors)
        write_or_check(NUCLEUS_ROOT / ".claude-plugin" / "marketplace.json", dump_json(marketplace(False, resolved)), args.write, errors)

    if errors:
        print("OpenAI adapter check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("OpenAI adapters are current." if args.check else "OpenAI adapters generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
