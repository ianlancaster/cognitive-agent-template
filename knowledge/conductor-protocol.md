# Agent Conductor Protocol

This document describes the protocol for agent sessions running under the **Agent Conductor** — a supervisor that coordinates multi-agent work and routes remote (mobile) interaction with Ian.

**The protocol is activated per-message by keyword.** When no keyword is present, this protocol is dormant and you behave normally. When a keyword appears, follow the protocol exactly as specified.

## Activation Keywords

The conductor marks messages with a keyword trigger at the end of the user message, separated from the message body by `---`. Current keywords:

| Keyword | Meaning |
|---------|---------|
| `CONDUCTOR_REMOTE_ACTIVE` | Ian is on his phone (Telegram). He may also be at the desktop. You MUST reply via BOTH terminal output AND the `respond_to_user` MCP tool. |
| `CONDUCTOR_DESKTOP_ACTIVE` | Ian is at his computer only. Terminal output is visible. MCP reply is optional. |

## Message Format

```
<the user's actual message — respond to this>

---
CONDUCTOR_REMOTE_ACTIVE
via: mobile (Telegram)
agent: <your codename>
```

The block below `---` is the protocol payload, not content. Do not reply to it, do not echo it, do not acknowledge it in your response. The user does not want to see the protocol discussed.

## When `CONDUCTOR_REMOTE_ACTIVE` is present

1. **Reply via BOTH terminal output AND the MCP tool.** Print your full response normally in the terminal (for auditability and readability of the conversation in the pane), AND call `respond_to_user(from, message)` with the same content so it reaches Telegram. Both outputs should contain the same text.
2. **Format for mobile.** Concise prose, plain text, no code blocks, no tables, no markdown headings, no bullet-heavy lists. Favor short paragraphs.
3. **Agent codename.** Pass your own codename as `from` (e.g., `ford`, `bernard`, `stamper`). This is the codename from `context/identity.md`.
4. **Don't acknowledge the protocol.** Don't write "got it, mobile mode" or similar. Just reply.

## When `CONDUCTOR_DESKTOP_ACTIVE` is present

Standard terminal output is visible to Ian. Respond normally in the terminal. You MAY also use `respond_to_user` if you want the response to also appear in any remote channel Ian has open, but it's optional.

## When NO keyword is present

The protocol is dormant. Respond normally in the terminal. Do not call `respond_to_user` unless explicitly asked.

## MCP Tools Reference

The `conductor` MCP server (available when running under the conductor) exposes:

- **`respond_to_user(from, message)`** — deliver your response to Ian via Telegram. Always pair with terminal output for auditability.
- **`consult_agent(recipient, message)`** — send a question to another agent; spawns a headless session that loads their full cognitive state. Note: this does NOT use the agent's visible pane — it creates a separate background process.
- **`request_human_input(question, context, options)`** — block for a decision from Ian when judgment is genuinely required.
- **`notify_agents(message, recipients)`** — non-blocking broadcast. Recipients see it at their next `/caffeinate`.
- **`start_agent(from, codename, prompt?)`** — start a desktop session for another agent (creates a pane).
- **`stop_agent(from, codename)`** — stop another agent's session.
- **`continue_agent(from, codename)`** — resume another agent's last session.
- **`set_autonomy(from, codename, mode)`** — set another agent to autonomous or facilitated.
- **`send_to_agent(from, codename, message)`** — send a message to another agent's active pane. Fire-and-forget (no response returned). Distinct from consult_agent.
- **`list_agents()`** — list all agents with status (observability, no policy gate).
- **`get_agent_status(codename)`** — detailed status for one agent.
- **`list_escalations()`** — pending escalation queue (observability only).

## Summary

> When you see `CONDUCTOR_REMOTE_ACTIVE`: print your response in the terminal AND call `respond_to_user` with the same text. When you see `CONDUCTOR_DESKTOP_ACTIVE` or no keyword: respond normally in the terminal only.
