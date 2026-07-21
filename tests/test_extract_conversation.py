import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "extract_conversation.py"
SPEC = importlib.util.spec_from_file_location("extract_conversation", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ExtractConversationTests(unittest.TestCase):
    def test_claude_keeps_dialogue_and_strips_host_and_tools(self):
        rendered = MODULE.render_session(ROOT / "tests/fixtures/claude-session.jsonl")
        self.assertIsNotNone(rendered)
        session, markdown = rendered

        self.assertEqual(session.provider, "claude")
        self.assertEqual(session.timestamp, "2026-07-01_1000")
        self.assertEqual(
            MODULE.output_name(session),
            "2026-07-01_1000_claude-session.md",
        )
        self.assertIn("Please remember that I prefer concise updates.", markdown)
        self.assertIn("I’ll keep updates concise.", markdown)
        self.assertIn("The preference is captured.", markdown)
        self.assertNotIn("system-reminder", markdown)
        self.assertNotIn("tool output", markdown)
        self.assertNotIn("private", markdown)

    def test_codex_keeps_user_and_agent_messages_only(self):
        rendered = MODULE.render_session(ROOT / "tests/fixtures/codex-session.jsonl")
        self.assertIsNotNone(rendered)
        session, markdown = rendered

        self.assertEqual(session.provider, "codex")
        self.assertEqual(session.session_id, "codex-test-session")
        self.assertEqual(session.timestamp, "2026-07-02_1100")
        self.assertEqual(
            MODULE.output_name(session),
            "2026-07-02_1100_codex_codex-test-session.md",
        )
        self.assertIn("Continue from our last reflection.", markdown)
        self.assertIn("I’m loading the persisted state.", markdown)
        self.assertIn("Ready. What’s on your mind?", markdown)
        self.assertNotIn("environment_context", markdown)
        self.assertNotIn("developer instructions", markdown)
        self.assertNotIn("tool output", markdown)
        self.assertNotIn("private", markdown)

    def test_atomic_write_replaces_existing_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "conversation.md"
            MODULE.atomic_write(output, "first")
            MODULE.atomic_write(output, "second")
            self.assertEqual(output.read_text(encoding="utf-8"), "second")

    def test_codex_discovery_excludes_subagent_threads(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            transcript = root / "subagent.jsonl"
            transcript.write_text(
                '{"type":"session_meta","payload":{"cwd":"%s","thread_source":{"subagent":{}}}}\n'
                % root,
                encoding="utf-8",
            )
            self.assertFalse(MODULE.codex_source_matches(transcript, root))


if __name__ == "__main__":
    unittest.main()
