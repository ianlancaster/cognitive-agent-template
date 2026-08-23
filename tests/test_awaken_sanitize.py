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


def repo_kind():
    """Tier detection: absent sync file = pristine base; else the kind field."""
    sync = ROOT / ".template-sync.json"
    if not sync.exists():
        return "base"
    import json
    return json.loads(sync.read_text(encoding="utf-8")).get("kind") or "base"


def allowlist_names(cmd):
    return set(re.findall(r'! -name "([^"]+)"', cmd)) - {".gitkeep"}


def run_sanitize_fixture(cmd):
    """Copy this repo's knowledge/, plant prior-agent junk, run the doc's own
    find command, return the surviving names."""
    with tempfile.TemporaryDirectory() as d:
        work = Path(d)
        shutil.copytree(ROOT / "knowledge", work / "knowledge")
        (work / "knowledge" / "research-notes.md").write_text("prior agent research\n")
        (work / "knowledge" / "campaign-x").mkdir()
        (work / "knowledge" / "campaign-x" / "plan.md").write_text("campaign plan\n")
        result = subprocess.run(["bash", "-c", cmd], cwd=work, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        return {p.name for p in (work / "knowledge").iterdir()}


class SanitizePreservesInfrastructure(unittest.TestCase):
    """Tier-aware: in BASE every tracked knowledge file is infrastructure, so
    survivors must EQUAL the tracked set (strict drift detection — adding a
    knowledge file without an allowlist entry fails here). In a ROLE TEMPLATE,
    tracked knowledge = infrastructure + role knowledge; Phase 0 deletes role
    knowledge and Phase 0.5 re-seeds it from the template, so the invariant is
    weaker: everything the allowlist names survives, planted junk does not.
    In an INSTANCE birth already happened — no invariant to check."""

    def test_sanitize_preserves_infrastructure(self):
        kind = repo_kind()
        if kind == "instance":
            self.skipTest("instance repo: sanitize ran at birth; instances "
                          "legitimately track non-infrastructure knowledge")
        cmd = knowledge_find_command(phase0_block(AWAKEN.read_text(encoding="utf-8")))
        survivors = run_sanitize_fixture(cmd)
        self.assertNotIn("research-notes.md", survivors)
        self.assertNotIn("campaign-x", survivors)
        if kind == "base":
            self.assertEqual(
                survivors,
                tracked_knowledge_files(),
                "Phase 0 allowlist and the base's tracked knowledge/ files have "
                "drifted apart: in base, every tracked file is infrastructure and "
                "must survive birth; everything else must be cleared.",
            )
        else:  # role-template (or flavored base): allowlist ⊆ survivors ⊆ tracked
            listed = allowlist_names(cmd) & tracked_knowledge_files()
            self.assertTrue(
                listed <= survivors,
                f"allowlist-named infrastructure deleted by sanitize: {listed - survivors}",
            )
            self.assertTrue(
                survivors <= tracked_knowledge_files(),
                f"untracked survivors: {survivors - tracked_knowledge_files()}",
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
