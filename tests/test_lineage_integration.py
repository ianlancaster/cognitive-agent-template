"""Integration test for the role-template lineage.

The /awaken ritual is agent-executed prose and cannot be run programmatically,
but the *invariants* it must produce can be. This builds a base -> role template
-> instance lineage on throwaway directories and asserts the per-tier metadata,
the marker semantics, and the leak-check gate — the mechanical core the ritual
relies on. It never touches a live agent's repo.
"""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "role-template.sh"


def rt(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class LineageTests(unittest.TestCase):
    def _role_template(self, root: Path) -> Path:
        """Simulate awaken Role-Template Onboarding T3/T4 on a throwaway dir."""
        rtpl = root / "role-template-researcher"
        # T1: a role template KEEPS the marker.
        write(rtpl / ".template-marker", "")
        # T3: portable cognition only — a role brief and a role-general belief
        # statement at held confidence, no history.
        write(rtpl / "context" / "role-brief.md",
              "# Researcher\nJob: retrieve and verify primary sources; never cite "
              "what was not retrieved.\n")
        write(rtpl / "memory" / "cognition" / "beliefs.md",
              "- Belief: an instrument that reports on the system it lives inside is "
              "vacuous until an ablation proves otherwise. Confidence: 2/5 (held, "
              "inherited from role template). What would change my mind: an ablation "
              "showing the instrument's structure does work.\n")
        # T4: role-template metadata.
        write(rtpl / ".template-sync.json", json.dumps({
            "kind": "role-template",
            "role": "researcher",
            "baseRemote": "https://github.com/example/cognitive-agent-template.git",
            "lastSyncedCommit": "9b53a58",
            "syncMode": "prompt",
            "contributionMode": "locked",
        }))
        return rtpl

    def test_role_template_invariants(self):
        with tempfile.TemporaryDirectory() as d:
            rtpl = self._role_template(Path(d))
            sync = rtpl / ".template-sync.json"
            self.assertEqual(rt("get", str(sync), "kind").stdout.strip(), "role-template")
            self.assertEqual(rt("get", str(sync), "role").stdout.strip(), "researcher")
            self.assertEqual(rt("get", str(sync), "contributionMode").stdout.strip(), "locked")
            # A template KEEPS its marker.
            self.assertTrue((rtpl / ".template-marker").exists())
            # Seeded cognition is leak-clean (no instance history rode along).
            self.assertEqual(rt("leak-check", str(rtpl / "context/role-brief.md")).returncode, 0)
            self.assertEqual(rt("leak-check", str(rtpl / "memory/cognition/beliefs.md")).returncode, 0)

    def test_instance_from_role_invariants(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rtpl = self._role_template(root)
            # Simulate instance-from-role: seed portable artifacts, then write
            # instance metadata (awaken Phase 0.5 + Phase 5).
            inst = root / "agent-newbie"
            write(inst / "context" / "role-brief.md",
                  (rtpl / "context/role-brief.md").read_text(encoding="utf-8"))
            # An instance DELETES the marker (it is a live agent).
            self.assertFalse((inst / ".template-marker").exists())
            write(inst / ".template-sync.json", json.dumps({
                "kind": "instance",
                "role": "researcher",
                "templateRemote": str(rtpl),
                "lastSyncedCommit": "9b53a58",
                "syncMode": "auto",
                "contributionMode": "approve",
                "lastContributedCommit": None,
            }))
            sync = inst / ".template-sync.json"
            self.assertEqual(rt("get", str(sync), "kind").stdout.strip(), "instance")
            self.assertEqual(rt("get", str(sync), "role").stdout.strip(), "researcher")
            # Instantiated from a role template -> may contribute back (approve).
            self.assertEqual(rt("get", str(sync), "contributionMode").stdout.strip(), "approve")
            self.assertEqual(rt("get", str(sync), "templateRemote").stdout.strip(), str(rtpl))

    def test_leak_gate_blocks_history_in_a_seed(self):
        with tempfile.TemporaryDirectory() as d:
            # A careless "portable" belief that smuggled a campaign in with it.
            bad = write(Path(d) / "beliefs.md",
                        "- Belief: stage risky changes. Evidence: during session 49 on "
                        "2026-07-30 the enforcement line closed at 200/200 units.\n")
            result = rt("leak-check", str(bad))
            self.assertEqual(result.returncode, 1, "leak-check must block a seed carrying history")
            self.assertIn("session 49", result.stdout)

    def test_migrate_then_opt_in_to_a_role(self):
        with tempfile.TemporaryDirectory() as d:
            sync = write(Path(d) / ".template-sync.json", json.dumps({
                "templateRemote": "https://github.com/example/cognitive-agent-template.git",
                "lastSyncedCommit": "9b53a58",
                "syncMode": "prompt",
            }))
            rt("migrate", str(sync))
            # Legacy agent lands locked; then the user deliberately assigns a role.
            self.assertEqual(rt("get", str(sync), "contributionMode").stdout.strip(), "locked")
            rt("set", str(sync), "role", "researcher")
            rt("set", str(sync), "contributionMode", "approve")
            self.assertEqual(rt("get", str(sync), "role").stdout.strip(), "researcher")
            self.assertEqual(rt("get", str(sync), "contributionMode").stdout.strip(), "approve")


if __name__ == "__main__":
    unittest.main()
