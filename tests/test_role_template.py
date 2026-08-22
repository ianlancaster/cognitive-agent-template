import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "role-template.sh"


def run(*args):
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


LEGACY_SYNC = {
    "templateRemote": "https://github.com/example/role-template-researcher.git",
    "lastSyncedCommit": "abc1234",
    "syncMode": "prompt",
    "lastSyncDate": "2026-07-30",
    "deferred": [],
}


class MigrateTests(unittest.TestCase):
    def _write(self, directory, data):
        path = Path(directory) / ".template-sync.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_migrate_adds_fields_with_safe_defaults(self):
        with tempfile.TemporaryDirectory() as d:
            path = self._write(d, LEGACY_SYNC)
            result = run("migrate", str(path))
            self.assertEqual(result.returncode, 0, result.stderr)
            after = json.loads(path.read_text(encoding="utf-8"))
            # New fields, conservative defaults: nothing flows up until enabled.
            self.assertEqual(after["kind"], "instance")
            self.assertIsNone(after["role"])
            self.assertEqual(after["contributionMode"], "locked")
            self.assertIsNone(after["lastContributedCommit"])
            # Existing fields preserved untouched.
            self.assertEqual(after["templateRemote"], LEGACY_SYNC["templateRemote"])
            self.assertEqual(after["lastSyncedCommit"], "abc1234")
            self.assertEqual(after["syncMode"], "prompt")

    def test_migrate_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            path = self._write(d, LEGACY_SYNC)
            run("migrate", str(path))
            # Flip contributionMode as if the user opted in, then migrate again.
            data = json.loads(path.read_text(encoding="utf-8"))
            data["contributionMode"] = "approve"
            path.write_text(json.dumps(data), encoding="utf-8")
            result = run("migrate", str(path))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("already-migrated", result.stdout)
            after = json.loads(path.read_text(encoding="utf-8"))
            # Migration must not clobber a user's later choice.
            self.assertEqual(after["contributionMode"], "approve")


class LeakCheckTests(unittest.TestCase):
    def _file(self, directory, text):
        path = Path(directory) / "candidate.md"
        path.write_text(text, encoding="utf-8")
        return path

    def test_clean_role_general_artifact_passes(self):
        with tempfile.TemporaryDirectory() as d:
            path = self._file(
                d,
                "A rule that constrains a concrete act binds; one that states a "
                "truth does not. Verify the far-end effect, not the near-end claim.",
            )
            result = run("leak-check", str(path))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("clean", result.stdout)

    def test_catches_planted_history(self):
        with tempfile.TemporaryDirectory() as d:
            path = self._file(
                d,
                "During session 50 on 2026-07-30 we killed 36/29 mutants and lost "
                "an hour trusting the dashboard.",
            )
            result = run("leak-check", str(path))
            # Nonzero return is the gate: a caller stops and reviews.
            self.assertEqual(result.returncode, 1)
            self.assertIn("POTENTIAL LEAK", result.stdout)
            self.assertIn("session 50", result.stdout)
            self.assertIn("2026-07-30", result.stdout)

    def test_extra_regex_catches_instance_specific_name(self):
        with tempfile.TemporaryDirectory() as d:
            path = self._file(
                d,
                "Route instrument review to a differently-positioned reviewer "
                "because Bernard is a different model family.",
            )
            # Structural patterns alone would miss a proper noun; the templatize
            # ritual supplies the instance's peer names as extra patterns.
            clean = run("leak-check", str(path))
            self.assertEqual(clean.returncode, 0, "no default pattern should match a bare name")
            flagged = run("leak-check", str(path), "Bernard")
            self.assertEqual(flagged.returncode, 1)
            self.assertIn("Bernard", flagged.stdout)


class GetSetTests(unittest.TestCase):
    def test_get_set_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / ".template-sync.json"
            path.write_text(json.dumps({"kind": "instance"}), encoding="utf-8")
            run("set", str(path), "role", "researcher")
            got = run("get", str(path), "role")
            self.assertEqual(got.stdout.strip(), "researcher")
            # Explicit JSON null round-trips as the string "null".
            run("set", str(path), "role", "null")
            got_null = run("get", str(path), "role")
            self.assertEqual(got_null.stdout.strip(), "null")


if __name__ == "__main__":
    unittest.main()
