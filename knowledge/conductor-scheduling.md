# Conductor Scheduling

When running managed, Agent Conductor can fire scheduled prompts at you (e.g., a nightly
`/sleep` or a morning `/caffeinate`). When schedules are configured, you don't need to
remember your own cadence — the conductor delivers each scheduled operation as an ordinary
prompt when it's due. No schedules exist by default.

## What the template owns

Schedule definitions, timing, and delivery are conductor configuration — not part of this
repository. What lives here is the behavior those prompts trigger:

- **Ad-hoc ritual additions.** If the user asks for something to happen as part of your
  morning routine, add it to `knowledge/caffeinate-additions.md`; your `/caffeinate` checks
  that file and executes anything listed. Same pattern for `knowledge/sleep-additions.md`
  and `/sleep`.
- **Fresh context.** A schedule may be configured with `freshContext` to start the ritual in
  a clean session rather than continuing an existing one. Rituals should work either way.

## Pausing

Before a long-running operation that a scheduled ritual would interrupt (an extended
research pass, a multi-hour experiment), temporarily suppress your schedules using the
pause/resume controls described by the injected conductor protocol, and resume them when
done. Prefer those controls over editing conductor configuration directly.

## Keeping scheduled rituals cheap

Scheduled rituals run unattended. Keep them focused — consolidation and state loading, not
open-ended new work. Anything expensive or judgment-heavy should be surfaced in the ready-up
for the user rather than launched from a scheduled session.
