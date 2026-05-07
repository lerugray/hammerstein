from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from hammerstein.context import ContextDisabled, build_project_context_preamble


class TestProjectContext(unittest.TestCase):
    def _init_git_repo(self, root: Path) -> None:
        subprocess.run(["git", "init"], cwd=str(root), check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(root), check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(root), check=True)
        (root / "README.md").write_text("Hello\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=str(root), check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["git", "commit", "-m", "init"], cwd=str(root), check=True, stdout=subprocess.DEVNULL)

    def test_minimal_includes_identity_and_docs(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir(parents=True)
            self._init_git_repo(root)
            (root / "MISSION.md").write_text("Mission statement\n", encoding="utf-8")
            (root / "CLAUDE.md").write_text("Rules\n", encoding="utf-8")
            # Uncommitted files should make the repo "dirty". Commit the docs so
            # identity reflects a clean tree for this test.
            subprocess.run(["git", "add", "."], cwd=str(root), check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["git", "commit", "-m", "add docs"], cwd=str(root), check=True, stdout=subprocess.DEVNULL)
            pre = build_project_context_preamble(
                mode="minimal",
                project_root=root,
                context_file=None,
            )
            self.assertIn("[PROJECT_CONTEXT mode=minimal]", pre)
            self.assertIn("repo_root: proj", pre)
            self.assertIn("branch:", pre)
            self.assertIn("head:", pre)
            self.assertIn("dirty: false", pre)
            self.assertIn("## MISSION.md", pre)
            self.assertIn("Mission statement", pre)
            self.assertIn("## CLAUDE.md", pre)

    def test_auto_discovers_state_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir(parents=True)
            self._init_git_repo(root)
            (root / ".hammerstein-state.md").write_text("State bullets\n", encoding="utf-8")
            pre = build_project_context_preamble(
                mode="minimal",
                project_root=root,
                context_file=None,
            )
            self.assertIn("## State (operator)", pre)
            self.assertIn("State bullets", pre)

    def test_context_file_outside_root_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir(parents=True)
            self._init_git_repo(root)
            outside = Path(td) / "outside.md"
            outside.write_text("hello", encoding="utf-8")
            with self.assertRaises(ContextDisabled):
                build_project_context_preamble(
                    mode="minimal",
                    project_root=root,
                    context_file=outside,
                )

    def test_possible_secret_aborts_injection(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir(parents=True)
            self._init_git_repo(root)
            # Looks like an API key.
            (root / "MISSION.md").write_text("sk-aaaaaaaaaaaaaaaaaaaaaaaaaaaa\n", encoding="utf-8")
            with self.assertRaises(ContextDisabled):
                build_project_context_preamble(
                    mode="minimal",
                    project_root=root,
                    context_file=None,
                )


if __name__ == "__main__":
    unittest.main()

