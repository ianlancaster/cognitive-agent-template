import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location("audit_template", Path(__file__).resolve().parents[1] / "scripts/audit_template.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TemplateAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.upstream = self.root / "template"
        self.local = self.root / "agent"
        self.upstream.mkdir()
        self.local.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        self.write(self.upstream, "COGNITIVE.md", "# Same heading\nOld body\n")
        self.write(self.local, "COGNITIVE.md", "# Same heading\nOld body\n")
        self.write(self.upstream, "scripts/removed.py", "old")
        self.write(self.local, "scripts/removed.py", "old")
        self.commit()
        self.base = self.git("rev-parse", "HEAD").strip()

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.upstream), *args], text=True)

    def write(self, root, path, content):
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-qm", "fixture")

    def test_full_content_addition_and_deletion_are_not_hidden_by_equal_pointer(self):
        self.write(self.upstream, "COGNITIVE.md", "# Same heading\nChanged body\n")
        self.write(self.upstream, ".claude/commands/new.md", "new command")
        (self.upstream / "scripts/removed.py").unlink()
        self.commit()
        result = MODULE.audit(self.local, self.upstream, self.base)
        self.assertFalse(result["complete"])
        self.assertEqual({row["file"] for row in result["files"] if row["status"] == "unresolved"},
                         {"COGNITIVE.md", ".claude/commands/new.md", "scripts/removed.py"})
        # Even a pointer already at the target cannot hide body drift or a missing addition.
        result = MODULE.audit(self.local, self.upstream, result["templateCommit"])
        self.assertFalse(result["complete"])

    def test_intentional_divergence_expires_when_either_side_changes(self):
        self.write(self.local, "COGNITIVE.md", "local role content")
        result = MODULE.audit(self.local, self.upstream, self.base)
        records = {r["file"]: r for r in result["files"]}
        records["COGNITIVE.md"].update(status="diverged-intentionally", reason="Preserve local role after integrating changes")
        self.assertTrue(MODULE.audit(self.local, self.upstream, self.base, records)["complete"])
        self.write(self.local, "COGNITIVE.md", "different role content")
        self.assertFalse(MODULE.audit(self.local, self.upstream, self.base, records)["complete"])
        self.write(self.local, "COGNITIVE.md", "local role content")
        self.write(self.upstream, "COGNITIVE.md", "changed upstream")
        self.commit()
        self.assertFalse(MODULE.audit(self.local, self.upstream, self.base, records)["complete"])

    def test_instance_memory_is_not_sync_owned(self):
        self.write(self.upstream, "memory/private.md", "template placeholder")
        self.write(self.local, "memory/private.md", "local experience")
        self.commit()
        result = MODULE.audit(self.local, self.upstream, self.base)
        self.assertTrue(result["complete"])
        self.assertNotIn("memory/private.md", [row["file"] for row in result["files"]])

    def test_cli_refuses_unresolved_content_and_accepts_matching_content(self):
        command = [sys.executable, "-B", str(Path(MODULE.__file__)), "--local", str(self.local),
                   "--template", str(self.upstream), "--base", self.base]
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
        self.write(self.local, "COGNITIVE.md", "# Same heading\nLost instruction\n")
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('"complete": false', result.stdout)


if __name__ == "__main__":
    unittest.main()
