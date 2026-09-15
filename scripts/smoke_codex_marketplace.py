#!/usr/bin/env python3
"""Install the complete Nucleus catalog into an isolated temporary Codex home.

The smoke test copies repository code only. It never resolves a user's config root,
starts Cortex MCP, or reads/writes real memory.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from catalog import PLUGIN_REPOSITORIES


NUCLEUS_ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = NUCLEUS_ROOT.parent
REPOSITORIES = [(name, repo) for name, repo, _ in PLUGIN_REPOSITORIES]


def run(argv: list[str], env: dict[str, str]) -> dict:
    completed = subprocess.run(
        argv,
        env=env,
        cwd=NUCLEUS_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"{' '.join(argv)} failed: {detail}")
    output = completed.stdout.strip()
    return json.loads(output) if output.startswith(("{", "[")) else {"output": output}


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="nucleus-codex-smoke-") as tmp_raw:
        tmp = Path(tmp_raw)
        market = tmp / "marketplace"
        plugins = market / "plugins"
        plugins.mkdir(parents=True)
        entries = []
        for plugin_name, repo_name in REPOSITORIES:
            source = LAB_ROOT / repo_name
            if not source.is_dir():
                raise RuntimeError(f"missing sibling repository: {source}")
            shutil.copytree(
                source,
                plugins / plugin_name,
                ignore=shutil.ignore_patterns(".git", "__pycache__", ".venv*", ".DS_Store"),
            )
            entries.append(
                {
                    "name": plugin_name,
                    "source": {"source": "local", "path": f"./plugins/{plugin_name}"},
                    "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                    "category": "Productivity",
                }
            )
        marketplace_path = market / ".agents" / "plugins" / "marketplace.json"
        marketplace_path.parent.mkdir(parents=True)
        marketplace_path.write_text(
            json.dumps(
                {"name": "nucleus", "interface": {"displayName": "Nucleus Fixture"}, "plugins": entries},
                indent=2,
            )
            + "\n"
        )

        home = tmp / "home"
        codex_home = tmp / "codex-home"
        home.mkdir()
        codex_home.mkdir()
        env = dict(os.environ)
        env.update({"HOME": str(home), "CODEX_HOME": str(codex_home)})
        run(["codex", "plugin", "marketplace", "add", str(market), "--json"], env)
        for plugin_name, _ in REPOSITORIES:
            run(["codex", "plugin", "add", f"{plugin_name}@nucleus", "--json"], env)
        listing = run(["codex", "plugin", "list", "--json"], env)
        serialized = json.dumps(listing)
        missing = [plugin_name for plugin_name, _ in REPOSITORIES if plugin_name not in serialized]
        if missing:
            raise RuntimeError("installed plugin listing missing: " + ", ".join(missing))
        print(f"Codex marketplace smoke passed: isolated install of all {len(REPOSITORIES)} Nucleus plugins.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
