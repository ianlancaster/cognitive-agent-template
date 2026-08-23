"""Per-class contributionMode + the authority floor + the candidates seam.

The authority floor is the load-bearing invariant from the Spartan integration
decisions (D1/D2/D3): a class named *-authority can NEVER be auto — set-mode
rejects it at write time and should-contribute clamps it at read time. The
.template-candidates seam lets a flavored base add portable paths as data,
not a script fork.
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


def sync_file(directory, mode):
    return write(Path(directory) / ".template-sync.json", json.dumps({
        "kind": "instance", "role": "researcher",
        "templateRemote": "https://example.com/role-template-researcher.git",
        "contributionMode": mode,
    }))


class AuthorityFloorTests(unittest.TestCase):
    def test_set_mode_rejects_auto_on_authority(self):
        with tempfile.TemporaryDirectory() as d:
            path = sync_file(d, "approve")
            r = rt("set-mode", str(path), "cognitive-authority", "auto")
            self.assertEqual(r.returncode, 2)
            self.assertIn("never be auto", r.stderr)
            # File unchanged: still the scalar.
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["contributionMode"], "approve")

    def test_set_mode_allows_auto_on_knowledge_and_converts_scalar(self):
        with tempfile.TemporaryDirectory() as d:
            path = sync_file(d, "approve")
            r = rt("set-mode", str(path), "cognitive-knowledge", "auto")
            self.assertEqual(r.returncode, 0, r.stderr)
            data = json.loads(path.read_text(encoding="utf-8"))
            # Scalar preserved as the map's default key.
            self.assertEqual(data["contributionMode"],
                             {"default": "approve", "cognitive-knowledge": "auto"})

    def test_lookup_clamps_authority_auto_defense_in_depth(self):
        with tempfile.TemporaryDirectory() as d:
            # A hand-edited config that snuck auto onto an authority class.
            path = sync_file(d, {"spartan-authority": "auto"})
            r = rt("should-contribute", str(path), "spartan-authority")
            self.assertEqual(r.returncode, 0)  # approve still permits contribution...
            self.assertIn("clamped to approve", r.stdout)  # ...but never as auto.
            self.assertIn("contributionMode=approve", r.stdout)


class PerClassLookupTests(unittest.TestCase):
    def test_map_lookup_and_default_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            path = sync_file(d, {"cognitive-knowledge": "auto", "default": "locked"})
            yes = rt("should-contribute", str(path), "cognitive-knowledge")
            self.assertEqual(yes.returncode, 0)
            self.assertIn("auto", yes.stdout)
            # Unlisted class falls back to default -> locked.
            no = rt("should-contribute", str(path), "cognitive-authority")
            self.assertEqual(no.returncode, 1)
            self.assertIn("locked", no.stdout)

    def test_absent_class_and_no_default_is_locked(self):
        with tempfile.TemporaryDirectory() as d:
            path = sync_file(d, {"cognitive-knowledge": "auto"})
            r = rt("should-contribute", str(path), "spartan-knowledge")
            self.assertEqual(r.returncode, 1)

    def test_map_without_class_arg_is_usage_error(self):
        with tempfile.TemporaryDirectory() as d:
            path = sync_file(d, {"cognitive-knowledge": "auto"})
            r = rt("should-contribute", str(path))
            self.assertEqual(r.returncode, 2)
            self.assertIn("class required", r.stderr)

    def test_scalar_still_works_without_class(self):
        with tempfile.TemporaryDirectory() as d:
            path = sync_file(d, "approve")
            self.assertEqual(rt("should-contribute", str(path)).returncode, 0)


class CandidatesSeamTests(unittest.TestCase):
    def test_template_candidates_file_extends_allowlist(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            git(repo, "init", "-q")
            git(repo, "config", "user.email", "t@e.com")
            git(repo, "config", "user.name", "t")
            write(repo / "memory" / "feedback_x.md", "rule\n")
            write(repo / "custom" / "portable.json", "{}\n")
            write(repo / "custom" / "data" / "local.json", "{}\n")
            git(repo, "add", "-A")
            git(repo, "commit", "-qm", "work")
            # Without the seam: only the base allowlist.
            out = rt("candidates", cwd=repo).stdout.splitlines()
            self.assertIn("memory/feedback_x.md", out)
            self.assertNotIn("custom/portable.json", out)
            # With the seam: extra pattern includes portable, still excludes data/.
            # ERE has no lookahead: scope the pattern to top-level custom/ files,
            # which structurally excludes custom/data/.
            write(repo / ".template-candidates",
                  "# flavored-base additions\n^custom/[^/]+\\.json$\n")
            git(repo, "add", "-A")
            git(repo, "commit", "-qm", "seam")
            out2 = rt("candidates", cwd=repo).stdout.splitlines()
            self.assertIn("custom/portable.json", out2)
            self.assertIn("memory/feedback_x.md", out2)


if __name__ == "__main__":
    unittest.main()
