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
import sys
from pathlib import Path


NUCLEUS_ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = NUCLEUS_ROOT.parent

PLUGINS = {
    "nucleus-router": {
        "version": "0.2.2",
        "display": "Nucleus Router",
        "short": "Route natural-language work to the right Nucleus capability",
        "long": "Use one natural-language front door to select and sequence installed Nucleus workflows across memory, operations, relationships, and planning.",
        "category": "Productivity",
        "capabilities": ["Read", "Interactive"],
        "prompts": ["What can Nucleus do?", "Route this request to the right workflow.", "Show the Nucleus command map."],
        "degraded": "If a referenced plugin is not installed, name the missing capability and offer the closest installed workflow. Never claim a route ran when it did not.",
    },
    "lead-engine": {
        "version": "0.2.5",
        "display": "Lead Engine",
        "short": "Turn live buying signals into reviewable outreach drafts",
        "long": "Capture and score buying signals, research contacts, draft warm outreach, manage follow-up cadence, and prepare call briefs without auto-sending.",
        "category": "Sales",
        "capabilities": ["Read", "Write", "Interactive"],
        "prompts": ["Show my lead pipeline.", "Draft a signal-based message for this person.", "Prepare a pre-call brief."],
        "degraded": "Apollo, LinkedIn, CRM, mail, and calendar access are optional connectors. Ask for pasted data or operate on local pipeline state when absent. Never simulate a connector or auto-send outreach.",
    },
    "weekly-alignment": {
        "version": "1.4.4",
        "display": "Weekly Alignment",
        "short": "Find cross-team overlaps, conflicts, and decision risks",
        "long": "Scan configured Slack sources for cross-team alignment signals and produce daily pulses, weekly reports, and risk updates.",
        "category": "Teamwork",
        "capabilities": ["Read", "Write"],
        "prompts": ["Scan Slack for alignment risks.", "Create this week's alignment report.", "Update our monitored risks."],
        "degraded": "A readable Slack app or MCP connector is required for scans. Without one, explain the dependency and stop; never invent channel activity. Previously saved local history may still be reviewed.",
        "skill_names": {"daily-pulse": "daily-pulse", "report": "report", "scan": "scan", "setup": "setup", "update-risks": "update-risks"},
    },
    "core-ops": {
        "version": "0.3.3",
        "display": "Core Ops",
        "short": "Run pipeline, delivery QA, diagnostics, and stack operations",
        "long": "Analyze CRM pipeline, review deliverables, inspect Nucleus health, record agent metrics, and register schedules when the host supports them.",
        "category": "Business",
        "capabilities": ["Read", "Write", "Interactive"],
        "prompts": ["Analyze my pipeline.", "Review this client deliverable.", "Diagnose my Nucleus setup."],
        "degraded": "CRM, document rendering, artifact, and scheduling capabilities are independent. Use available inputs, produce Markdown when rich artifacts are unavailable, and provide schedule definitions without claiming registration when no scheduler exists.",
    },
    "news-curator": {
        "version": "0.2.4",
        "display": "News Curator",
        "short": "Research and draft a cited weekly news roundup",
        "long": "Find recent stories, rank them for a configured audience, and assemble a voice-matched roundup with traceable sources.",
        "category": "Research",
        "capabilities": ["Read", "Interactive"],
        "prompts": ["Research this week's top stories.", "Draft my weekly roundup.", "Configure my roundup audience."],
        "degraded": "Web search is required for fresh research. Mail/newsletter connectors are optional. If delegation is unavailable, run the curator and assembler stages inline and preserve source citations.",
    },
    "project-setup": {
        "version": "0.2.5",
        "display": "Project Setup",
        "short": "Initialize a client engagement from one guided interview",
        "long": "Create an engagement plan, portable AI workspace prompt, folder blueprint, next action, and optional Cortex nodes from approved inputs.",
        "category": "Productivity",
        "capabilities": ["Read", "Write", "Interactive"],
        "prompts": ["Set up a new client project.", "Configure my engagement templates.", "Create a kickoff plan for this engagement."],
        "degraded": "When Drive or project-creation APIs are absent, return a folder blueprint and a host-neutral workspace prompt for manual creation. Cortex writes are optional and require confirmation.",
    },
    "time-tracking": {
        "version": "0.2.4",
        "display": "Time Tracking",
        "short": "Classify calendar time and prepare reviewable invoices",
        "long": "Turn calendar events into a local, reviewable time log and generate invoice drafts from configured client billing rules.",
        "category": "Business",
        "capabilities": ["Read", "Write"],
        "prompts": ["Track yesterday's billable time.", "Generate this month's invoice drafts.", "Configure my billing rules."],
        "degraded": "A calendar connector is optional: accept pasted events when absent. Generate Markdown or structured invoice data if document tooling is unavailable. Never send invoices automatically.",
    },
    "client-status": {
        "version": "0.2.5",
        "display": "Client Status",
        "short": "Draft client updates from approved work context",
        "long": "Synthesize project, calendar, CRM, and Cortex context into concise weekly client-status drafts for user review.",
        "category": "Business",
        "capabilities": ["Read", "Write"],
        "prompts": ["Draft this week's client updates.", "Create a status update for this client.", "Configure my status-update format."],
        "degraded": "Use whichever approved sources are available and list skipped sources. Ask for missing project facts when evidence is insufficient. Draft only; never send without a separate explicit action and confirmation.",
    },
    "referral-engine": {
        "version": "0.2.5",
        "display": "Referral Engine",
        "short": "Surface timely referral opportunities and draft the ask",
        "long": "Review relationship context, cooling periods, and positive moments to prioritize referral actions and draft voice-matched asks.",
        "category": "Sales",
        "capabilities": ["Read", "Write"],
        "prompts": ["Show this week's referral opportunities.", "Draft a referral ask for this person.", "Configure my referral rules."],
        "degraded": "CRM, mail, calendar, and Cortex are optional evidence sources. Use available local context, name skipped sources, honor cooling periods, and never auto-send an ask.",
    },
    "relationships": {
        "version": "0.2.4",
        "display": "Relationships",
        "short": "Prioritize relationship actions and draft useful touchpoints",
        "long": "Build a daily relationship cockpit, rebalance a network, and create context-aware touchpoint drafts from shared identity, voice, and memory.",
        "category": "Sales",
        "capabilities": ["Read", "Write", "Interactive"],
        "prompts": ["Build today's relationship brief.", "Draft a touchpoint for this person.", "Rebalance my relationship network."],
        "degraded": "Cortex, CRM, mail, and research connectors enrich ranking but are optional. Run read-only role work inline when agents are unavailable. All outbound content remains a draft.",
        "skill_names": {"setup": "setup"},
    },
    "writing-style": {
        "version": "0.1.3",
        "display": "Writing Style",
        "short": "Draft in your voice and learn from approved edits",
        "long": "Create voice-matched drafts, compare drafts with final edits, and propose durable style-rule updates only after repeated evidence.",
        "category": "Writing",
        "capabilities": ["Read", "Write"],
        "prompts": ["Write this in my voice.", "Learn from these edits.", "Review my current style rules."],
        "degraded": "Mail and publishing connectors are optional. Accept pasted samples and return copy-ready text when absent. Never send or publish automatically; style-file changes require user approval.",
    },
    "daily-brief": {
        "version": "0.6.2",
        "display": "Daily Brief",
        "short": "Build and process a daily operating brief",
        "long": "Combine calendar, tasks, outreach, inbox, CRM, and Cortex context into a daily brief, then process user-approved annotations and plan tomorrow.",
        "category": "Productivity",
        "capabilities": ["Read", "Write", "Interactive"],
        "prompts": ["Build today's brief.", "Process these brief annotations.", "Plan my next business day."],
        "degraded": "Cowork's interactive artifact is not portable. In ChatGPT and Codex, write a Markdown snapshot and use pasted or local annotation state. Missing connectors are listed and skipped; no mail, CRM, or calendar mutation occurs without confirmation.",
    },
}

ALIASES = {
    "lead-engine": ["lead-brief", "lead-capture", "lead-connect", "lead-draft", "lead-log", "lead-pipeline", "lead-pull", "lead-setup", "lead-warm"],
    "core-ops": ["setup-core"],
    "news-curator": ["setup-news"],
    "project-setup": ["setup-projects"],
    "time-tracking": ["setup-time"],
    "client-status": ["setup-status"],
    "referral-engine": ["setup-referrals"],
    "relationships": ["setup-relationships"],
    "writing-style": ["setup-style", "style"],
    "daily-brief": ["setup-brief"],
}

AGENTS = {
    "lead-engine": ["contact-researcher"],
    "core-ops": ["pipeline-analyst", "pipeline-forecast"],
    "news-curator": ["news-curator", "post-assembler"],
    "relationships": ["relationship-ranker"],
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


def manifest(name: str, data: dict[str, object]) -> dict[str, object]:
    return {
        "name": name,
        "version": data["version"],
        "description": data["long"],
        "author": {"name": "BrightWay AI", "url": "https://brightwayai.com"},
        "license": "MIT",
        "homepage": f"https://github.com/BrightWayAI/{name}",
        "repository": f"https://github.com/BrightWayAI/{name}",
        "keywords": ["nucleus", "chatgpt", "codex"],
        "skills": "./skills/",
        "interface": {
            "displayName": data["display"],
            "shortDescription": data["short"],
            "longDescription": data["long"],
            "developerName": "BrightWay AI",
            "category": data["category"],
            "capabilities": data["capabilities"],
            "websiteURL": f"https://github.com/BrightWayAI/{name}",
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
Identity and voice remain shared files at `<config-root>/identity.md` and
`<config-root>/voice.md`. Plugin state belongs under `<config-root>`—normally
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

{data['degraded']}

Always report unavailable or skipped capabilities in the result. A degraded run must
remain useful where possible, but it must never imply that missing data was read or an
external action happened.
"""


def wrapper_md(repo: Path, name: str, command: str) -> str:
    desc = command_description(repo / "commands" / f"{command}.md", command)
    extra = "\nAlso read `../lead-engine/SKILL.md` for the shared signal, voice, and cadence methodology.\n" if name == "lead-engine" else ""
    yaml_description = json.dumps(desc, ensure_ascii=False)
    return f"""---
name: {command}
description: {yaml_description}
---

# {command}

Read `../../references/openai-portability.md`, then read
`../../commands/{command}.md` completely and follow it as the canonical workflow.
Treat `/{command}`, `${command}`, natural-language activation, and the ChatGPT plugin
mention as equivalent entrypoints. Ignore Claude-only tool allowlists and model names;
apply the capability translation and degradation rules from the portability contract.
{extra}
Do not duplicate or reinterpret the command here. Preserve its confirmation gates,
draft-only boundaries, file locations, and output contract.
"""


def agent_toml(name: str, role: str) -> str:
    descriptions = {
        "contact-researcher": "Research one contact or company and return a cited dossier without writing external systems.",
        "pipeline-analyst": "Read and rank CRM pipeline evidence without changing CRM or local state.",
        "pipeline-forecast": "Build an evidence-based pipeline forecast without changing source systems.",
        "news-curator": "Research and rank recent news candidates with citations.",
        "post-assembler": "Assemble approved news candidates into a voice-matched draft.",
        "relationship-ranker": "Rank relationship actions from available evidence without writing or sending.",
    }
    return f'''name = "{role}"
description = "{descriptions[role]}"
sandbox_mode = "read-only"
developer_instructions = """
Read AGENTS.md, references/openai-portability.md, and agents/{role}.md completely.
Treat Claude model/tool metadata as source-host examples. Use only connector and web
capabilities actually available, explicitly list skipped sources, and never fabricate
evidence. Return findings to the parent. Do not write local state, mutate connectors,
send messages, or schedule work. If delegation is unavailable, the parent must follow
the same role inline with this read-only boundary.
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


def update_claude_manifest(repo: Path, version: str, write: bool, errors: list[str]) -> None:
    path = repo / ".claude-plugin" / "plugin.json"
    value = json.loads(path.read_text())
    value["version"] = version
    write_or_check(path, dump_json(value), write, errors)


def marketplace(native: bool) -> dict[str, object]:
    entries = []
    for repo_name, data in PLUGINS.items():
        if native:
            entry_name = repo_name
            source = {"source": "url", "url": f"https://github.com/BrightWayAI/{repo_name}.git"}
            category = data["category"]
            entries.append({
                "name": entry_name,
                "source": source,
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": category,
            })
        else:
            entries.append({
                "name": repo_name,
                "version": data["version"],
                "source": {"source": "github", "repo": f"BrightWayAI/{repo_name}"},
                "description": data["long"],
                "author": {"name": "BrightWay AI"},
            })
    cortex_native = {
        "name": "cortex",
        "source": {"source": "url", "url": "https://github.com/BrightWayAI/claude-cortex.git"},
        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        "category": "Productivity",
    }
    cortex_claude = {
        "name": "claude-cortex",
        "version": "4.15.0",
        "source": {"source": "github", "repo": "BrightWayAI/claude-cortex"},
        "description": "A host-portable Markdown second brain shared by Claude, ChatGPT Work, and Codex.",
        "author": {"name": "BrightWay AI"},
    }
    entries.insert(1, cortex_native if native else cortex_claude)
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
    marker = f"## [{version}] — OpenAI host adapter"
    if marker in text:
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

    for name, data in PLUGINS.items():
        repo = LAB_ROOT / name
        if not repo.is_dir():
            errors.append(f"missing sibling repository: {repo}")
            continue
        write_or_check(repo / ".codex-plugin" / "plugin.json", dump_json(manifest(name, data)), args.write, errors)
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
        update_claude_manifest(repo, str(data["version"]), args.write, errors)
        update_changelog(repo, str(data["version"]), args.write, errors)
        update_readme(repo, data, args.write, errors)

    write_or_check(NUCLEUS_ROOT / ".agents" / "plugins" / "marketplace.json", dump_json(marketplace(True)), args.write, errors)
    write_or_check(NUCLEUS_ROOT / ".claude-plugin" / "marketplace.json", dump_json(marketplace(False)), args.write, errors)

    if errors:
        print("OpenAI adapter check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("OpenAI adapters are current." if args.check else "OpenAI adapters generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
