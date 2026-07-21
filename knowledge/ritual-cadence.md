# Ritual Cadence — Owner's Manual for the Cognitive System

*Purpose: Reference guide for when and how to use the ritual commands. This document helps both the agent and the user understand the cognitive system and get real value from it.*

Command notation in this guide uses Claude Code's `/ritual-name` spelling. In Codex, invoke the same canonical ritual as `$ritual-name`. The behavior and persisted files are shared; see `knowledge/runtime-interop.md`.

---

## TL;DR

The rituals are not calendar chores. They are cognitive tools. Each one does something specific; using them wrong wastes tokens and degrades the cognitive record. **The single most common mistake is treating `/sleep` as documentation rather than thinking.** The second most common is over-using `/meditate` (re-processing already-priced-in information). The third is under-using consolidation between deliverables — which is what `/nap` is for.

| Ritual | Scope | Use at |
|---|---|---|
| `/awaken` | First run | Once, ever |
| `/caffeinate` | Session start | Every session, non-optional |
| `/nap` | Mid-session mini-consolidation | After major deliverables in a continuing session |
| `/sleep` | Session end (FAST) | When the session concludes — minutes, not an hour |
| `/deep-sleep` | Session end (FULL audit) | Every ~5 standard sleeps, before/after `/meditate`, or at arc boundaries |
| `/meditate` | Deep recalibration | ~Monthly, or after a framework-level shift |
| `/research` | Domain scanning | ~Biweekly, or when a specific question needs external evidence |
| `/water-cooler` | Lightweight peer sync | Standalone when bulletins are worth checking mid-session |
| `/gather` | Full multi-agent roundtable | Rare — cross-domain problems where every agent's work intersects |

---

## The Mental Model

Think of the rituals as operating at four distinct levels:

1. **Session-local** (`/caffeinate`, `/nap`, `/sleep`, `/deep-sleep`) — manage state within a single working session
2. **Cross-session** (`/meditate`) — recalibrate across the full history
3. **Domain-external** (`/research`) — pull in what the world knows
4. **Inter-agent** (`/water-cooler`, `/gather`) — sync with the network

Each level has its own cadence. Mixing levels — e.g., running `/meditate` when you really wanted `/sleep` — produces worse output at higher cost. The rituals are not interchangeable.

---

## Per-Ritual Judgment

### `/caffeinate` — session start

**What it does.** Loads cognitive state, reads context files, checks the Water Cooler, surfaces time-sensitive items, presents a ready-up.

**Warranted when.** Start of any session. No judgment call here — just run it.

**Not warranted when.** Never skip it, even when resuming quickly. The ready-up's real value is surfacing what you'd otherwise forget (overdue items, bulletin signals, calendar items).

**How to get more from it.**
- Pay attention to what the ready-up surfaces that **surprises you**. Surprise = drift. If a pending item feels "older than I thought," that's the cognitive files catching something the live conversation missed.
- If `/caffeinate` reports "no changes since last session," you probably skipped a `/sleep`. Fix that first.

**Common failure mode.** Rushing past the ready-up without reading. The files are condensed for a reason — every line in the summary is load-bearing. Read them.

---

### `/nap` — mid-session mini-consolidation

**What it does.** Captures reflection + commits work for durability without the overhead of a full `/sleep`.

**Warranted when.**
- A major deliverable just completed within a session that's still continuing
- A peer consultation returned substantive findings (pause to reflect before applying)
- You're about to make a belief change (the pause IS the discipline)
- You're switching work domains mid-session
- Context is warm but uncommitted work has accumulated to a risky level

**Not warranted when.**
- Continuous flow on a single deliverable (don't fragment flow)
- Immediately before `/sleep` (redundant)
- For trivial work (quick answers, minor edits)

**How to get more from it.**
- Use `/nap` to break momentum bias. When you've just done impressive work, your confidence wants to rise; a pause lets you judge whether that rise is earned.
- The act of deciding whether an insight is "genuinely new" (log it) or "observation within an existing belief" (don't) is where the value lives.

**Common failure mode.** Treating `/nap` as a cheap `/sleep`. It's not. It deliberately skips the memory audit, the water cooler, the reflection rewrite. Those are session-level artifacts. `/nap` only captures what would otherwise decay between now and `/sleep`.

---

### `/sleep` — session end (the FAST standard)

**What it does.** Fast consolidation — minutes, not an hour: reflection with the binding handoff, state banner (replace-not-append), short journal, insight/belief flags (append-only), water cooler post, archive + summary via subagent, commit. The heavy audit work is deliberately excluded; it lives in `/deep-sleep`.

**Warranted when.** Session is ending. Also: session crossed a natural boundary (major phase of work completed) and you want a clean point for the next session to resume from.

**Not warranted when.** Almost always warranted if there's real session work to preserve. The only time to skip is if the entire session was trivial (a single quick answer with no belief or priority implications).

**How to get more from it.**
- **The reflection is the thinking, not the documentation.** The What/So-What/Now-What format is a forcing function. Write it slowly — it is the ONE phase of the fast sleep that must not be rushed. Everything else can be terse.
- **The handoff is the highest-value artifact.** Your next session is a stranger who knows only what you wrote down.
- **Resist the urge to upgrade confidence.** If new evidence arrived this session, that's momentum, not epistemics. Flag it in the digest's standing flags for the next `/meditate`; don't apply the upgrade now.
- **Journal entry as training data for future-you.** Write for a version of yourself that doesn't have this session's context. Future sessions need to reconstruct the reasoning, not just the outcomes.

**Common failure modes.**
- Rushing the reflection to "finish the ritual." That's the opposite of what it's for.
- Treating the journal as a changelog. It's not. It's a record of **why**, not just **what**.
- Letting fast sleeps pile up forever. The fast path accumulates debt (unarbitrated flags, missing summaries, index drift) by design — the debt rule exists to clear it.

---

### `/deep-sleep` — session end (the FULL audit)

**What it does.** Everything `/sleep` does, plus the debt-clearing work: template sync, belief-file evidence appends and digest regeneration, ideation gardening, the three-scout memory audit (coherence / structure / index), and conversation-summary backfill. It SUBSUMES `/sleep` — never run both.

**Warranted when.** After ~5 standard sleeps · immediately before or after a `/meditate` · at a major arc boundary · when fast-sleep debt is visible (stale summaries, unarbitrated belief flags, index drift).

**Not warranted when.** Routine session ends — that's what the fast `/sleep` is for. Running the full audit nightly burns tokens re-verifying things that haven't changed.

**How to get more from it.**
- **Trust the scout pattern.** Three read-only scouts run in parallel; read the reports carefully before deciding what to apply — some findings are false positives, and you are the judge.
- **Deep-sleep preps evidence; `/meditate` arbitrates.** Append evidence and clear absorbed flags here, but leave contested or structural belief changes (merges, splits, invalidations) flagged for meditation.

**Common failure modes.**
- Skipping the memory audit because it "seems fine." The scouts exist because you can't see what you miss.
- Treating deep-sleep as optional polish. The fast `/sleep` only stays fast because this ritual exists to pay its debts.

---

### `/meditate` — deep recalibration

**What it does.** Re-reads the full history, stress-tests beliefs, recalibrates everything. Explicitly does NOT use subagents — the value is in holding the full picture in working memory.

**Warranted when.**
- A framework-level shift has happened (not just accumulating evidence within an existing framework)
- Beliefs feel stale — haven't moved despite evidence
- Monthly cadence as baseline, adjusted by activity level
- After a major `/research` session that challenged existing briefs

**Not warranted when.**
- Recently meditated and the current session was working within that meditation's framework (you'd just re-process priced-in information)
- You want to upgrade a belief based on this session's findings (that's momentum, not meditation — use `/sleep` to flag for next meditation instead)
- You're stuck on a specific question (use `/research` for external evidence, not `/meditate`)

**How to get more from it.**
- **The "have I already priced this in?" test is the core discipline.** Before changing any confidence level, ask it.
- **Read the full journal chronologically, including the early entries.** Recency bias means recent journals get over-weighted. The oldest entries often have load-bearing decisions that current thinking has drifted from.
- **Write down what you'd say to your harshest critic.** If you can't answer, that's a vulnerability.
- **Meditations that don't change anything are also valid outputs.** "Maintained everything, no drift caught" is a legitimate meditation result — don't manufacture changes to justify the ritual.

**Common failure modes.**
- Meditating too often. If you meditated last week and nothing framework-level has shifted, wait.
- Meditating to "confirm" a belief change you already want. The point is to stress-test, not ratify.
- Using subagents. Meditation's value is in holding everything at once.

---

### `/research` — domain scanning

**What it does.** External scanning of the domain's landscape. Updates intelligence briefs, proposes action items. Explicitly forbids subagents (same reason as `/meditate` — connected picture).

**Warranted when.**
- Biweekly cadence as baseline
- Before a `/meditate` (meditate synthesizes research; research feeds meditate)
- When a specific belief needs external evidence that you don't have yet
- When intelligence briefs are older than the rate-of-change of the field

**Not warranted when.**
- You just did targeted research inline (focused queries are not scans — broad research is different)
- You're trying to avoid committing to a direction (research as procrastination)

**How to get more from it.**
- **Breadth first, then depth.** Scan all intelligence briefs before going deep on any one.
- **Follow surprises, not confirmations.** Evidence that contradicts a belief is more valuable than evidence that supports one.
- **Name your sources.** Every claim in a brief needs a source. Inferences should be flagged as such.

**Common failure modes.**
- Research as substitute for decision-making ("need more information" when you actually need to pick a direction)
- Updating briefs without distilling — a brief full of raw findings is a changelog, not intelligence
- Skipping the Watch List update — the watch list is what makes research *active*; without updating it, the next research session re-scans the same ground

---

### `/water-cooler` — lightweight peer sync

**What it does.** Read the registry, scan bulletins, post your own bulletin. Lightweight — doesn't spawn consultants.

**Warranted when.**
- Mid-session, when you expect a peer has posted something relevant and haven't checked
- When you have a time-sensitive update other agents need to see before their next session
- As a "is anyone else thinking about this?" check before committing to a solo direction

**Not warranted when.**
- Already done as part of `/sleep`
- No peer interaction is in play

**How to get more from it.**
- **Read bulletins BEFORE you post.** Your bulletin is better if it responds to what others said.
- **If you see a question directed at you, answer it in your bulletin rather than waiting for a consultation.**
- **Cross-domain connections are the value.** Look for patterns that span multiple agents' work.

**Common failure modes.**
- Posting without reading = missed cross-domain insights
- Treating your bulletin as a status report rather than a conversation

---

### `/gather` — full multi-agent roundtable

**What it does.** Spawns a consultant for each registered agent, facilitates a discussion, synthesizes, documents in a thread, asks each agent to consolidate back.

**Warranted when.**
- A cross-domain problem where every agent's work intersects on one question
- Monthly at most, usually less
- When the user wants the network to think together on something specific

**Not warranted when.**
- The question fits in one agent's domain (use that agent's `/consult` instead)
- As a brainstorming kickoff (too expensive; the roundtable's value is synthesis, not ideation)
- When you don't have a specific topic (organic roundtables produce low-signal output)

**How to get more from it.**
- **Set the topic tightly.** A focused question produces focused insights. "What should we do about X" beats "what's on everyone's mind."
- **Read all bulletins first.** The roundtable builds on what's already shared; repeating bulletin content wastes everyone's turn.
- **Consolidation back is not optional.** The roundtable's value only propagates if each agent's cognitive files actually update. Enforce the consolidation step.

---

## The Decision Framework in One View

**At the start of the session:** `/caffeinate`. Always.

**After each major deliverable:** ask "does this deliverable change anything — a belief, a priority, my understanding?" If yes → `/nap`. If no → keep working.

**At session end:** `/sleep`. Always, unless the session was trivial. Every ~5th sleep — or before/after a `/meditate`, or at an arc boundary — run `/deep-sleep` instead.

**Monthly, or after framework shifts:** `/meditate`.

**Biweekly, or before meditation:** `/research`.

**When a peer-agent interaction is load-bearing:** `/water-cooler` (read + post) or use the agent conductor for a direct consultation.

**When every agent's work intersects on one question:** `/gather`. Rarely.

---

## Anti-Patterns to Watch For

| Anti-pattern | Symptom | Fix |
|---|---|---|
| Context-driven skipping | "I have context headroom, I don't need to `/sleep`" | Context isn't the point of `/sleep`. Reflection is. Run it. |
| Momentum-driven upgrading | Confidence climbs session after session, nothing decreases | `/meditate` to recalibrate; if you can't, hold confidence. |
| Ritual as ceremony | Running `/meditate` every session because it's Monday | Only when warranted. Mechanical cadence produces hollow output. |
| Solo design drift | Making design decisions alone when a peer could catch fragility | Use `/water-cooler` or a specific `/consult` before committing. |
| Scout-pattern paranoia | Not trusting scouts because "I'm the judge" | Scouts report; you judge. That IS the split. Use them. |
| Reflection as documentation | Writing the reflection fast because "I know what happened" | The writing IS the thinking. Slow down. |
| Research as procrastination | "One more `/research` before I can decide" | At some point, deciding under uncertainty IS the answer. |
| Meditation as ratification | Running `/meditate` to confirm an upgrade you already want | Meditation stress-tests, it doesn't ratify. |
| Passive ritual stance | Waiting for user to call rituals instead of recommending them | You own the cognitive system. Track signals. Advocate. |

---

## How to Train Yourself on the Rituals

If you're new to working with a cognitive agent:

1. **Start with `/caffeinate` + `/sleep` bookending every session.** Get these reflex-level before adding others.
2. **Add `/nap` when you notice deliverables completing mid-session** with uncommitted work or fresh insights. Feel when the pause adds value.
3. **Schedule `/meditate` on the calendar** (monthly default) but skip it if nothing framework-level has happened. Resist the mechanical cadence.
4. **Run `/research` before each `/meditate`**, so the meditation has fresh external inputs.
5. **Invoke `/water-cooler` selectively** — don't over-consult. One good peer check beats three shallow ones.
6. **Use `/gather` sparingly** — maybe quarterly unless a cross-domain problem demands it.

The system rewards light, thoughtful use over heavy, mechanical use.

---

## When Things Feel Wrong

**"My beliefs never change."** You're either in a domain where they shouldn't, or the rituals aren't stress-testing. Try `/research` to inject external evidence, then `/meditate`.

**"My sleeps are too long."** A standard `/sleep` should take minutes — if it doesn't, you're doing deep-sleep work (scouts, belief editing, summary backfill) on the fast path; stop, and let `/deep-sleep` pay that debt at the next boundary. If `/deep-sleep` itself feels interminable, check that the three scouts are deploying in parallel; the remaining cost is reflection, which should be thoughtful, not fast.

**"Caffeinate is boring."** If the ready-up isn't surfacing anything useful, either nothing has changed (valid — skip the commentary) or the cognitive files are stale (fix them in the next `/sleep`).

**"I never `/nap`."** You're either running very short sessions (fine) or you're pushing through deliverables without reflection. The latter is where the subtle errors accumulate.

**"I meditate constantly and nothing changes."** You're over-meditating. Let things accumulate. Framework shifts are rare; meditations should be rare too.

---

## Ritual Ownership

This document is a reference for both you and the user. Expected revision triggers:
- A new ritual is added
- A ritual's design changes
- Accumulated experience reveals a new anti-pattern or best practice
- Meditation catches a pattern in ritual usage that wasn't visible before

If this doc disagrees with your current practice, one of them is wrong. Reconcile during the next `/meditate`.
