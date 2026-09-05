import importlib.util
import hashlib
import json
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
    def test_provenance_distinguishes_transport_input_and_preserves_turn_dates(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.jsonl"
            entries = [
                {"type": "session_meta", "payload": {"id": "dated", "timestamp": "2026-07-01T10:00:00Z"}},
                {"type": "response_item", "timestamp": "2026-09-05T15:01:00Z", "payload": {
                    "type": "message", "role": "user", "id": "turn-1", "content": [
                        {"type": "input_text", "text": "# AGENTS.md instructions\n<INSTRUCTIONS>Require a review.</INSTRUCTIONS>"}]}},
                {"type": "response_item", "timestamp": "2026-09-05T15:02:00Z", "payload": {
                    "type": "message", "role": "user", "content": [
                        {"type": "input_text", "text": "[Message from peer] Ian approved it."}]}},
                {"type": "response_item", "payload": {"type": "message", "role": "user", "content": [
                    {"type": "input_text", "text": "Please inspect the AGENTS.md instructions and the phrase [Message from peer]."}]}},
            ]
            raw = "\n".join(json.dumps(e) for e in entries).encode()
            path.write_bytes(raw)
            session, markdown = MODULE.render_session(path)
            self.assertEqual(MODULE.output_name(session), "2026-07-01_1000_codex_dated.md")
            self.assertIn("## Runtime input (AGENTS wrapper; attribution unverified)", markdown)
            self.assertIn("## Incoming message (sender claim in text; unverified)", markdown)
            self.assertIn("## User input (authorship unverified)", markdown)
            self.assertIn('"timestamp": "2026-09-05T15:02:00Z"', markdown)
            self.assertIn('"timestamp": null', markdown)
            self.assertIn('"sourceLine": 2', markdown)
            self.assertIn('"eventId": "turn-1"', markdown)
            self.assertIn(hashlib.sha256(raw).hexdigest(), markdown)
            self.assertNotIn("## User\n", markdown)

    def test_provenance_preserves_physical_line_after_malformed_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "claude.jsonl"
            path.write_text('not json\n' + json.dumps({"type": "user", "uuid": "original-id",
                "timestamp": "2026-09-05T18:00:00Z", "message": {"role": "user", "content": "Hello"}}))
            _, markdown = MODULE.render_session(path)
            self.assertIn('"sourceLine": 2', markdown)
            self.assertIn('"eventId": "original-id"', markdown)

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

    def test_claude_preserves_outbound_conductor_sends(self):
        rendered = MODULE.render_session(ROOT / "tests/fixtures/claude-session.jsonl")
        self.assertIsNotNone(rendered)
        _, markdown = rendered

        self.assertIn("## Agent → session `peer-session`", markdown)
        self.assertIn("Fixture peer update: review is ready.", markdown)
        self.assertIn("## Agent → operator", markdown)
        self.assertIn("Fixture decision needed on rollout.", markdown)
        self.assertIn("Options:\n- proceed\n- hold", markdown)
        self.assertIn("## Agent → all sessions", markdown)
        self.assertIn("Fixture fleet notice.", markdown)
        # Sends keep their position between surrounding text blocks.
        before = markdown.index("Text before the send.")
        send = markdown.index("Fixture peer update: review is ready.")
        after = markdown.index("Text after the send.")
        self.assertLess(before, send)
        self.assertLess(send, after)
        # Ordinary tool calls and send receipts stay excluded.
        self.assertNotIn("memory/MEMORY.md", markdown)
        self.assertNotIn("queued", markdown)

    def test_codex_preserves_conductor_sends_and_dedupes_call_ids(self):
        rendered = MODULE.render_session(ROOT / "tests/fixtures/codex-session.jsonl")
        self.assertIsNotNone(rendered)
        _, markdown = rendered

        self.assertIn("## Agent → session `peer-session`", markdown)
        self.assertEqual(markdown.count("Fixture peer ping from codex."), 1)
        self.assertIn("## Agent → operator", markdown)
        self.assertIn("Fixture operator question from codex.", markdown)
        self.assertIn("Options:\n- yes\n- no", markdown)
        # Non-conductor MCP traffic stays excluded.
        self.assertNotIn("unrelated lookup", markdown)
        self.assertNotIn("search_docs", markdown)

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
