"""Phase 0 sanitization must preserve template infrastructure.

The awaken ritual's Phase 0 clears agent-specific knowledge with a find
allowlist. The template's own tracked knowledge/ files ARE the infrastructure
set — so these tests extract the find command from awaken.md's fenced block
(the exact command an awakening agent executes, never a re-implementation) and
assert the survivors equal the tracked set. Adding a knowledge file to the
template without extending the allowlist fails this suite immediately —
the defect class that silently deleted infrastructure docs at every birth.
"""

import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AWAKEN = ROOT / ".claude" / "commands" / "awaken.md"


def phase0_block(text):
    """The Phase 0 'Files and directories to clear' fenced bash block."""
    section = text.split("## Phase 0: Sanitize Inherited State", 1)[1]
    section = section.split("### Files to explicitly preserve", 1)[0]
    blocks = re.findall(r"```bash\n(.*?)```", section, re.DOTALL)
    assert blocks, "no fenced bash block found in Phase 0"
    return blocks[0]


def knowledge_find_command(block):
    m = re.search(r"^find knowledge .*?-exec rm -rf \{\} \+$", block, re.DOTALL | re.MULTILINE)
    assert m, "no find-knowledge command found in Phase 0 block"
    return m.group(0)


def tracked_knowledge_files():
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "knowledge"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    return {Path(p).name for p in out}


class SanitizePreservesInfrastructure(unittest.TestCase):
    def test_tracked_knowledge_survives_sanitize(self):
        cmd = knowledge_find_command(phase0_block(AWAKEN.read_text(encoding="utf-8")))
        with tempfile.TemporaryDirectory() as d:
            work = Path(d)
            shutil.copytree(ROOT / "knowledge", work / "knowledge")
            # Plant agent-specific content a prior agent would have left behind.
            (work / "knowledge" / "research-notes.md").write_text("prior agent research\n")
            (work / "knowledge" / "campaign-x").mkdir()
            (work / "knowledge" / "campaign-x" / "plan.md").write_text("campaign plan\n")

            result = subprocess.run(["bash", "-c", cmd], cwd=work, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

            survivors = {p.name for p in (work / "knowledge").iterdir()}
            self.assertEqual(
                survivors,
                tracked_knowledge_files(),
                "Phase 0 allowlist and the template's tracked knowledge/ files have "
                "drifted apart: every tracked file is infrastructure and must survive "
                "birth; everything else must be cleared.",
            )

    def test_phase0_block_is_glob_free(self):
        # zsh aborts a command on an unmatched glob (`rm -rf plans/*` on a repo
        # with no plans/), so the Phase 0 block must not rely on shell globs.
        block = phase0_block(AWAKEN.read_text(encoding="utf-8"))
        offenders = [
            line for line in block.splitlines()
            if not line.lstrip().startswith("#") and re.search(r"rm (-\S+ )*\S*\*", line)
        ]
        self.assertEqual(offenders, [], f"glob-dependent rm in Phase 0 block: {offenders}")


if __name__ == "__main__":
    unittest.main()
