"""End-to-end lineage dogfood — the system's thesis in one test.

Builds a role template and an instance as real git repos, has the instance
learn a portable lesson (tangled with history) plus pure history, runs the
/deep-sleep up-contribution flow's mechanical steps (candidates -> distill ->
leak-check -> apply), and asserts the capstone invariant:

    the distilled lesson reaches the template; NONE of the instance's history does.

Everything is throwaway; no live agent is touched.
"""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "role-template.sh"


def rt(*args, cwd=None):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True,
                          cwd=str(cwd) if cwd else None)


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def init_repo(repo):
    Path(repo).mkdir(parents=True, exist_ok=True)  # git -C needs the dir to exist
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "t")


class EndToEndLineageTests(unittest.TestCase):
    def test_lesson_travels_history_does_not(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)

            # --- Role template: definitional, keeps marker, holds only portable cognition.
            tmpl = root / "role-template-researcher"
            init_repo(tmpl)
            write(tmpl / ".template-marker", "")
            write(tmpl / "context" / "role-brief.md", "# Researcher\nVerify before citing.\n")
            write(tmpl / ".template-sync.json", json.dumps({
                "kind": "role-template", "role": "researcher",
                "baseRemote": "https://github.com/example/cognitive-agent-template.git",
                "contributionMode": "locked",
            }))
            git(tmpl, "add", "-A")
            git(tmpl, "commit", "-qm", "role template seed")

            # --- Instance: spawned from the role template.
            inst = root / "agent-newbie"
            init_repo(inst)
            write(inst / ".template-sync.json", json.dumps({
                "kind": "instance", "role": "researcher",
                "templateRemote": str(tmpl),
                "contributionMode": "auto",
                "lastContributedCommit": None,
            }))
            git(inst, "add", "-A")
            git(inst, "commit", "-qm", "instance birth")
            base = git(inst, "rev-parse", "HEAD").stdout.strip()

            # --- The instance works a campaign and learns.
            # A portable lesson, but tangled with history (names, dates, a project).
            write(inst / "memory" / "feedback_delivery.md",
                  "During session 49 on 2026-07-30, Bernard pointed out we trusted a "
                  "'sync complete' flag before row counts matched and lost an hour.\n")
            # Pure history — must never travel.
            write(inst / "journal" / "2026-07-30.md", "Long day. Bernard reviewed everything.\n")
            write(inst / "memory" / "project_bicam.md", "The BICAM enforcement campaign plan.\n")
            git(inst, "add", "-A")
            git(inst, "commit", "-qm", "a session's work")

            # --- /deep-sleep phase 5.5, mechanically.
            # Gate: auto instance with a role and a template -> may contribute.
            self.assertEqual(rt("should-contribute", str(inst / ".template-sync.json")).returncode, 0)

            # 1. candidates: the portable file, not the history.
            cands = rt("candidates", base, cwd=inst).stdout.splitlines()
            self.assertIn("memory/feedback_delivery.md", cands)
            self.assertNotIn("journal/2026-07-30.md", cands)
            self.assertNotIn("memory/project_bicam.md", cands)

            # 2. distill (what the ritual/agent produces): story stripped, act-shaped.
            distilled = ("A signal that reports dispatch ('sync complete', 'sent') is not "
                         "evidence of effect. Verify the far-end state, not the near-end claim.\n")

            # 3. leak-check the distilled artifact with the instance's proper nouns.
            staged = write(root / "staged_feedback_delivery.md", distilled)
            self.assertEqual(
                rt("leak-check", str(staged), "Bernard", "BICAM").returncode, 0,
                "a properly distilled artifact must pass the leak gate")
            # And prove the RAW artifact would have been blocked (history caught).
            self.assertEqual(
                rt("leak-check", str(inst / "memory/feedback_delivery.md"), "Bernard", "BICAM").returncode, 1,
                "the raw, un-distilled artifact must be blocked")

            # 4. apply (auto): the distilled artifact lands in the template; commit there.
            write(tmpl / "memory" / "feedback_delivery.md", distilled)
            git(tmpl, "add", "-A")
            git(tmpl, "commit", "-qm", "contribution from agent-newbie: delivery lesson")

            # 5. record.
            head = git(inst, "rev-parse", "HEAD").stdout.strip()
            rt("set", str(inst / ".template-sync.json"), "lastContributedCommit", head)
            self.assertEqual(
                rt("get", str(inst / ".template-sync.json"), "lastContributedCommit").stdout.strip(), head)

            # --- The capstone invariant: lesson in, history NOT.
            template_text = "\n".join(
                p.read_text(encoding="utf-8")
                for p in tmpl.rglob("*") if p.is_file() and ".git" not in p.parts
            )
            self.assertIn("far-end state", template_text, "the distilled lesson must reach the template")
            for leaked in ("Bernard", "session 49", "2026-07-30", "BICAM", "row counts"):
                self.assertNotIn(leaked, template_text, f"instance history leaked to template: {leaked!r}")
            # The template still holds no journal, no project file.
            self.assertFalse((tmpl / "journal").exists())
            self.assertFalse((tmpl / "memory" / "project_bicam.md").exists())
            # And it is still a template.
            self.assertTrue((tmpl / ".template-marker").exists())


if __name__ == "__main__":
    unittest.main()
