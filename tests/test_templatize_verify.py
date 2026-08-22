"""Phase 3 Verify-gate test.

/templatize's Verify step leak-checks every seeded file with the instance's
proper nouns supplied as extra patterns — because a distilled rule can keep a
bare peer name that no structural pattern would catch (runbook failure mode #1).
This simulates an assembled role template with three clean distillates and one
that smuggled a name through, and asserts the gate flags exactly the leaky one.
"""

import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "role-template.sh"


def leak_check(path, *extra):
    return subprocess.run(
        ["bash", str(SCRIPT), "leak-check", str(path), *extra],
        capture_output=True, text=True,
    )


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class TemplatizeVerifyTests(unittest.TestCase):
    def test_verify_flags_only_the_leaky_distillate(self):
        with tempfile.TemporaryDirectory() as d:
            dest = Path(d) / "role-template-researcher"
            clean = [
                write(dest / "context" / "role-brief.md",
                      "# Researcher\nRetrieve and verify primary sources; never cite "
                      "what was not retrieved.\n"),
                write(dest / "memory" / "feedback_review.md",
                      "Route instrument review to a differently-positioned reviewer — "
                      "one blind to how the instrument was built. It catches what is "
                      "invisible from inside your own context.\n"),
                write(dest / "memory" / "cognition" / "beliefs.md",
                      "- Belief: an instrument reporting on the system it lives inside "
                      "is vacuous until an ablation proves otherwise. Confidence: 2/5 "
                      "(held). Would change my mind: an ablation showing it does work.\n"),
            ]
            # Failure mode #1: a distilled rule that kept a bare peer name.
            leaky = write(dest / "memory" / "feedback_leaky.md",
                          "Route review to a fresh reviewer because Bernard is a "
                          "different model family and sees what you cannot.\n")

            # The instance's proper nouns, collected in templatize Pre-flight.
            names = ["Bernard", "Stubbs", "Ian"]

            # Verify loop: every clean distillate passes...
            for f in clean:
                r = leak_check(f, *names)
                self.assertEqual(r.returncode, 0, f"{f} should be clean:\n{r.stdout}")

            # ...and the leaky one is flagged, by name.
            r = leak_check(leaky, *names)
            self.assertEqual(r.returncode, 1, "the smuggled name must be caught")
            self.assertIn("Bernard", r.stdout)

    def test_structural_patterns_alone_miss_the_bare_name(self):
        # Demonstrates *why* proper nouns are supplied: without them the leak
        # survives, which is the whole reason Verify collects names in Pre-flight.
        with tempfile.TemporaryDirectory() as d:
            leaky = write(Path(d) / "feedback_leaky.md",
                          "Route review to a fresh reviewer because Bernard sees what "
                          "you cannot.\n")
            without_names = leak_check(leaky)
            self.assertEqual(without_names.returncode, 0, "structural patterns miss a bare name")
            with_names = leak_check(leaky, "Bernard")
            self.assertEqual(with_names.returncode, 1)


if __name__ == "__main__":
    unittest.main()
