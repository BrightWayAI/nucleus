"""Canonical active Nucleus plugin catalog used by release and Codex tooling."""

from __future__ import annotations


# (Codex/native name, sibling repository directory, Claude marketplace name)
PLUGIN_REPOSITORIES = (
    ("cortex", "cortex", "cortex"),
    ("alignment", "alignment", "alignment"),
    ("ops", "ops", "ops"),
    ("research", "research", "research"),
    ("clients", "clients", "clients"),
    ("admin", "admin", "admin"),
    ("growth", "growth", "growth"),
    ("comms", "comms", "comms"),
    ("briefing", "briefing", "briefing"),
)

PLUGIN_NAMES = tuple(name for name, _, _ in PLUGIN_REPOSITORIES)
REPOSITORY_NAMES = tuple(repo for _, repo, _ in PLUGIN_REPOSITORIES)
CLAUDE_PLUGIN_NAMES = tuple(claude for _, _, claude in PLUGIN_REPOSITORIES)
REPOSITORY_BY_PLUGIN = {name: repo for name, repo, _ in PLUGIN_REPOSITORIES}
CLAUDE_NAME_BY_PLUGIN = {name: claude for name, _, claude in PLUGIN_REPOSITORIES}
