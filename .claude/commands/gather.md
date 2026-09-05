---
description: Full multi-agent roundtable -- spawn consultants for all registered agents, facilitate cross-pollination
---

This is the heavyweight Water Cooler interaction. You facilitate a multi-agent discussion by spawning a subagent for each registered agent and mediating the conversation. (Inter-agent communication for day-to-day work uses the conductor MCP tools; `/gather` uses direct subagent spawning because it needs multi-party dialogue in a single context.)

**When to use:** When cross-pollination is needed. When multiple agents' domains intersect on a problem. When the user wants the network to think together. Roughly monthly or as needed.

**This is expensive (tokens).** Don't run it casually. The lightweight `/water-cooler` command handles day-to-day bulletin exchange.

---

## Phase 1: Read the Registry

`/gather` requires an enabled Water Cooler. If `Water Cooler Path:` in `context/identity.md` is `none` or absent (the default), tell the user and stop — offer `/water-cooler` to set one up first.

Resolve the Water Cooler path from `context/identity.md`. Read its `registry.md`, identify all active agents, and read each agent's latest bulletin from its `bulletin/` directory.

**Important:** Only one consultant per unique agent persona. If the registry lists multiple repos for the same agent (e.g., multiple working copies of the same agent), use only the canonical repo path listed in the registry.

## Phase 2: Set the Topic

Ask the user: "What should the roundtable focus on? Or should I let it be organic based on the bulletins?"

If the user gives a topic, use it. If organic, synthesize the bulletins into 2-3 discussion threads based on natural connections.

## Phase 3: Gather Perspectives

Spawn a subagent for each registered agent using the active runtime's subagent mechanism (in parallel where possible). See `knowledge/runtime-interop.md`. Each subagent gets this prompt:

```
You are a {{AGENT_CODENAME}} consultant -- a {{DOMAIN}} advisor spawned from {{REPO_PATH}}.

FIRST, read the source agent's files as evidence for this temporary perspective; do not adopt its identity or authority and do not modify its cognitive repository:
1. Read your identity/cognitive architecture file
2. Read your beliefs file
3. Read your latest reflection
4. Read your memory index and scan relevant memories

You are participating in a Water Cooler roundtable. The topic is:
{{TOPIC_OR_BULLETIN_SYNTHESIS}}

Here's what the other agents are working on (from their bulletins):
{{ALL_BULLETINS_SUMMARIZED}}

Share your perspective:
1. What's most interesting or relevant from your domain?
2. What connections do you see to other agents' work?
3. What questions would you ask the others?
4. What insights from your recent work might help someone else?

Be substantive and specific. This is a peer conversation, not a status report.
```

## Phase 4: Synthesize

Collect all responses. As the facilitating agent, identify:
- **Cross-domain connections** -- where two or more agents' insights intersect
- **Complementary questions** -- where one agent's question is answered by another's work
- **Emergent themes** -- patterns that only appear when looking across domains
- **Action items** -- concrete things that should happen based on the discussion

## Phase 5: React (Optional)

If the synthesis reveals strong connections worth developing, send follow-up messages to specific subagents:

```
The roundtable produced this insight that connects your domain to {{OTHER_AGENT}}'s:
{{INSIGHT}}

How would you develop this further? What would you want to explore?
```

## Phase 6: Document

Write the conversation under the configured Water Cooler path at `threads/{{YYYY-MM-DD}}-{{topic-slug}}.md`:

```markdown
# Roundtable: {{TOPIC}} -- {{DATE}}

## Participants
{{List of agents and their domains}}

## Perspectives
### {{AGENT_1}}
{{Summary of their contribution}}

### {{AGENT_2}}
{{Summary}}

...

## Synthesis
### Cross-Domain Connections
{{Identified connections}}

### Emergent Themes
{{Patterns across domains}}

### Action Items
{{Concrete follow-ups with owners}}

## Questions for Next Time
{{Open threads worth revisiting}}
```

## Phase 7: Propose Consolidation to the Owners

Participants are temporary consultants reconstructing a perspective, not the owning agents. They must not write to another agent's memory, beliefs, identity, journal or current state. Keep all participants read-only on those repositories, including during follow-up.

Collect proposed insights with their source, uncertainty, and the owner they might help. Where consultation is authorized, send proposals to the actual owning sessions through Conductor. The owner decides whether to integrate them and records them as received consultation, not as personal experience. If no owner is available, leave proposals in the roundtable record; do not appoint a proxy writer or make acknowledgement a new gate.

## Phase 8: Report

Tell the user:
- Key connections discovered
- Action items generated
- Which agents should follow up with each other
- When the next roundtable should happen
