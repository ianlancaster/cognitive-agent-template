import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AwakenSanitationTests(unittest.TestCase):
    def test_actual_phase_zero_preserves_required_contracts_and_clears_instance_history(self):
        # Execute the documented deletion block only in a disposable fixture.
        ritual = (ROOT / ".claude/commands/awaken.md").read_text()
        block = ritual.split("### Files and directories to clear", 1)[1].split("```bash\n", 1)[1].split("```", 1)[0]
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            shutil.copytree(ROOT / "knowledge", fixture / "knowledge")
            for path in ["memory/cognition", "memory/intelligence", "context", "plans", "journal", "conversations"]:
                (fixture / path).mkdir(parents=True)
            for path in ["knowledge/old-agent-research.md", "memory/feedback_old.md", "plans/old.md", ".template-marker"]:
                (fixture / path).write_text("inherited state")
            subprocess.run(["bash", "-e", "-c", block], cwd=fixture, check=True, capture_output=True)
            for name in ["current-state-contract.md", "durability.md", "runtime-interop.md"]:
                self.assertEqual((fixture / "knowledge" / name).read_bytes(), (ROOT / "knowledge" / name).read_bytes())
            for path in ["knowledge/old-agent-research.md", "memory/feedback_old.md", "plans/old.md", ".template-marker"]:
                self.assertFalse((fixture / path).exists())


if __name__ == "__main__":
    unittest.main()
