"""Phase 4 tests: the up-contribution gate and candidate lister.

should-contribute is the gate /deep-sleep checks before doing any up-sync work;
candidates is the worklist. Together they enforce two hard requirements the
yield measurement established: locked/role-less instances never contribute, and
a session that changed only instance-only files is a graceful no-op.
"""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "role-template.sh"


def rt(*args, cwd=None):
    return subprocess.run(
        ["bash", str(SCRIPT), *args], capture_output=True, text=True,
        cwd=str(cwd) if cwd else None,
    )


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class ShouldContributeTests(unittest.TestCase):
    def _sync(self, directory, **fields):
        base = {
            "kind": "instance",
            "role": "researcher",
            "templateRemote": "https://github.com/example/role-template-researcher.git",
            "contributionMode": "approve",
        }
        base.update(fields)
        path = Path(directory) / ".template-sync.json"
        path.write_text(json.dumps(base), encoding="utf-8")
        return path

    def test_instance_with_role_and_approve_may_contribute(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(rt("should-contribute", str(self._sync(d))).returncode, 0)

    def test_auto_may_contribute(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(rt("should-contribute", str(self._sync(d, contributionMode="auto"))).returncode, 0)

    def test_locked_may_not(self):
        with tempfile.TemporaryDirectory() as d:
            r = rt("should-contribute", str(self._sync(d, contributionMode="locked")))
            self.assertEqual(r.returncode, 1)
            self.assertIn("locked", r.stdout)

    def test_no_role_may_not(self):
        with tempfile.TemporaryDirectory() as d:
            r = rt("should-contribute", str(self._sync(d, role=None)))
            self.assertEqual(r.returncode, 1)
            self.assertIn("no role", r.stdout)

    def test_role_template_may_not_contribute_up(self):
        with tempfile.TemporaryDirectory() as d:
            r = rt("should-contribute", str(self._sync(d, kind="role-template")))
            self.assertEqual(r.returncode, 1)
            self.assertIn("only instances", r.stdout)


class CandidatesTests(unittest.TestCase):
    def _repo(self, directory):
        repo = Path(directory)
        git(repo, "init", "-q")
        git(repo, "config", "user.email", "t@example.com")
        git(repo, "config", "user.name", "t")
        write(repo / "README.md", "seed\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "baseline")
        return repo, git(repo, "rev-parse", "HEAD").stdout.strip()

    def test_lists_portable_candidates_excludes_instance_only(self):
        with tempfile.TemporaryDirectory() as d:
            repo, base = self._repo(d)
            # A portable candidate and two instance-only files, all new since base.
            write(repo / "memory" / "feedback_review.md", "a general rule\n")
            write(repo / "memory" / "cognition" / "beliefs.md", "- Belief: x\n")
            write(repo / "journal" / "2026-08-22.md", "what happened today\n")
            write(repo / "memory" / "project_campaign.md", "this campaign only\n")
            git(repo, "add", "-A")
            git(repo, "commit", "-qm", "work")
            out = rt("candidates", base, cwd=repo).stdout.splitlines()
            self.assertIn("memory/feedback_review.md", out)
            self.assertIn("memory/cognition/beliefs.md", out)
            # Instance-only files must never appear.
            self.assertNotIn("journal/2026-08-22.md", out)
            self.assertNotIn("memory/project_campaign.md", out)

    def test_graceful_no_op_when_only_history_changed(self):
        with tempfile.TemporaryDirectory() as d:
            repo, base = self._repo(d)
            write(repo / "journal" / "2026-08-22.md", "history only\n")
            write(repo / "context" / "current-state.md", "state only\n")
            git(repo, "add", "-A")
            git(repo, "commit", "-qm", "history")
            out = rt("candidates", base, cwd=repo).stdout.strip()
            self.assertEqual(out, "", "a history-only session must yield no candidates")


if __name__ == "__main__":
    unittest.main()
