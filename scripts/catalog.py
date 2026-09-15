"""Canonical active Nucleus plugin catalog used by release and Codex tooling."""

from __future__ import annotations


# (Codex/native name, sibling repository directory, Claude marketplace name)
PLUGIN_REPOSITORIES = (
    ("cortex", "claude-cortex", "claude-cortex"),
    ("weekly-alignment", "weekly-alignment", "weekly-alignment"),
    ("core-ops", "core-ops", "core-ops"),
    ("news-curator", "news-curator", "news-curator"),
    ("delivery", "delivery", "delivery"),
    ("time-tracking", "time-tracking", "time-tracking"),
    ("relationships", "relationships", "relationships"),
    ("voice", "voice", "voice"),
    ("daily-brief", "daily-brief", "daily-brief"),
)

PLUGIN_NAMES = tuple(name for name, _, _ in PLUGIN_REPOSITORIES)
REPOSITORY_NAMES = tuple(repo for _, repo, _ in PLUGIN_REPOSITORIES)
CLAUDE_PLUGIN_NAMES = tuple(claude for _, _, claude in PLUGIN_REPOSITORIES)
REPOSITORY_BY_PLUGIN = {name: repo for name, repo, _ in PLUGIN_REPOSITORIES}
CLAUDE_NAME_BY_PLUGIN = {name: claude for name, _, claude in PLUGIN_REPOSITORIES}
