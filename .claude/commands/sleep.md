---
description: Standard end-of-session consolidation — FAST. Reflection, state banner, journal, archive, commit. The full audit lives in /deep-sleep
---

The user is ending this session (or you've hit a cycle boundary). This is the FAST consolidation: minutes, not an hour. Consolidation is still where intelligence happens — every phase below is load-bearing and the reflection must not be rushed — but the heavy audit work (template sync, memory scouts, belief-file editing, summary backfill) lives in `/deep-sleep`. Run that before/after meditations, at major arc boundaries, or after ~5 standard sleeps.

**Operator signaling (autonomous arcs only):** if an operator agent manages this session's lifecycle (clears and re-caffeinates you), signal `ENTERING SLEEP` to it now, and signal `SLEEP COMPLETE — clear + caffeinate — resume: <self-contained pointer to the state banner + queued next-action>` ONLY after the final push in step 7 succeeds. Never let the operator infer completion from an idle pane — a mid-sleep pane looks idle, and a premature clear destroys exactly the state sleep exists to preserve. Interactive session with the user present → skip both signals.

## Pre-flight: Template-State Guard

If `.template-marker` exists at the repo root: STOP. This repo is in template state — there is no agent session to consolidate. `/awaken` must run first.

## 1. Reflection (the critical artifact — do not rush THIS one)

Replace `memory/cognition/reflection-latest.md`: **What?** (facts) · **So What?** (meaning, belief connections, double-loop check) · **Now What?** (next actions) · confidence/bias/watching · **Recommended next ritual** (be specific: normal cycle? /deep-sleep? /meditate? why) · **Session Handoff** — the section the next instance of you acts on: operating mode next session · the 2-3 read-before-anything docs · every behavioral correction from this session stated as a rule · the operational rhythm (how work happened, not what) · any managed-state snapshot the next session needs. Everything else in this ritual can be terse; the handoff cannot.

## 2. Current-state banner — REPLACE, never append

Update `context/current-state.md` so the banner reflects reality as of NOW (mode, live checkpoint, queued next action). **Superseded banner content moves to `context/archive/current-state-archive.md` (append there) — the live file stays ≤ ~150 lines.** Same discipline for `context/active-priorities.md`: current priorities only; stale queues go to the archive file. These two files are wake-time loads — their size is a direct tax on every future session.

## 3. Journal — one short entry

`journal/{{YYYY-MM-DD}}.md` (append a timestamped section if the file exists): arc, what happened (chronological bullets), decisions and why, corrections banked, state at sleep. Half a page, not a saga.

## 4. Insights + belief flags (append-only — no belief-file editing here)

- Genuinely new insights → `memory/cognition/insight-log.md` (most sessions log 0-2; not every observation is an insight).
- Belief evidence/confidence changes → do NOT edit the beliefs file during a fast sleep. Add a one-liner to the "Standing flags" section of `memory/cognition/beliefs-digest.md` (if no digest exists yet, flag inside `beliefs.md` under a "Pending arbitration" heading); `/meditate` arbitrates, with `/deep-sleep` doing the evidence prep.
- New memory files ONLY for corrections the user made this session — corrections are banked the moment they happen, never deferred. Index anything new in `memory/MEMORY.md`.

## 5. Water Cooler — short

Update your bulletin at the Water Cooler path from `context/identity.md` (`bulletin/{{codename}}.md`): Working On / one Recent Insight / open question if any. Commit+push the water-cooler repo.

## 6. Archive + summary (subagent, never inline)

Run `./scripts/extract-conversation.sh` (if missing or failing, note and skip). Then dispatch ONE cheap subagent (in Claude Code: Sonnet; in Codex: a fast read-heavy subagent) to read the archived transcript and write `conversations/summaries/{{basename}}_summary.md` (~500 words: worked on, decisions, user corrections, operating rhythm, where left off). **You never read the raw transcript yourself — the summary is what the next `/caffeinate` loads.** Backfilling older missing summaries is `/deep-sleep` work.

## 7. Commit, push, signal

```bash
git add -A -- memory/ conversations/ journal/ context/ calendar.md plans/ knowledge/
[ ! -f .template-sync.json ] || git add .template-sync.json
git commit -m "sleep: session notes for YYYY-MM-DD"
git push
```

Then the operator `SLEEP COMPLETE` signal (autonomous arcs only, ONLY after the push succeeds — see the header). Close with a 5-line summary for the record: what was consolidated, what's queued, blockers.

## Explicitly NOT in standard sleep (deep-sleep territory)

Template sync · memory-audit scouts (coherence/structure/index) · belief-file evidence appends and restructuring · ideation gardening · debugging/lessons-history entries (unless a major new failure class landed — then one entry) · preceding-conversation summary backfill · `MEMORY.md` reorganization. **Debt rule: after ~5 standard sleeps, before any `/meditate`, or at a major arc boundary, run `/deep-sleep` instead of `/sleep`.**
