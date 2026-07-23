# Agent Conductor Protocol (Pointer)

The operational protocol for managed sessions — tool names, messaging semantics, lifecycle
controls, and transport rules — is **owned by Agent Conductor and injected at runtime**:

- **Claude Code:** appended to the system prompt at launch.
- **Codex:** written into the managed section of `AGENTS.override.md` (regenerated on every
  launch; gitignored).

**Do not duplicate the conductor's tool inventory or transport rules in this repository.**
Injected instructions are always current; copies here rot and then conflict. When this file
and the injected protocol disagree, the injected protocol wins.

The few stable facts safe to state here:

- Inbound communication arrives in envelopes: `[Message from <sender>]` and
  `[Broadcast from <sender>]`. Handle the content, then continue your work.
- Your identity is mechanical — the conductor knows who you are from your connection.
  Never sign your own messages or claim to be another session.
- If no conductor protocol was injected this session, you are running standalone: there are
  no conductor tools, and you simply operate solo.
