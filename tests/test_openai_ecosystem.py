from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_openai_ecosystem import check_active_architecture  # noqa: E402


class ActiveArchitectureGuardTests(unittest.TestCase):
    def test_rejects_retired_runtime_state_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            command = repo / "commands" / "broken.md"
            command.parent.mkdir()
            command.write_text(
                "Read `<config-root>/plugins/lead-engine.pipeline.md`.\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            check_active_architecture(repo, errors)
            self.assertEqual(len(errors), 1)
            self.assertIn("retired plugin state path", errors[0])

    def test_allows_explicit_legacy_compatibility_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            command = repo / "commands" / "migration.md"
            command.parent.mkdir()
            command.write_text(
                "Read `<config-root>/plugins/lead-engine.user-context.md` once. "
                "<!-- LEGACY_COMPAT -->\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            check_active_architecture(repo, errors)
            self.assertEqual(errors, [])

    def test_rejects_direct_cowork_identity_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            skill = repo / "skills" / "broken" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("Read `~/Documents/Claude/identity.md`.\n", encoding="utf-8")
            errors: list[str] = []
            check_active_architecture(repo, errors)
            self.assertEqual(len(errors), 1)
            self.assertIn("pre-scope identity", errors[0])

    def test_rejects_hard_coded_memory_default_in_root_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "README.md").write_text(
                "Memory lives at `~/Documents/Claude/memory/`.\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            check_active_architecture(repo, errors)
            self.assertEqual(len(errors), 1)
            self.assertIn("pre-resolver memory path", errors[0])


if __name__ == "__main__":
    unittest.main()
