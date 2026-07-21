# Conductor Scheduling

You have scheduled operations managed by the Agent Conductor. These run automatically via cron — you don't need to remember to sleep or caffeinate.

## Your Schedule Config

Your cron schedules are defined in:
`/Users/ianlancaster/Projects/agents/agent-conductor/config/agents/{your-codename}.yaml`

The conductor re-reads this file every 5 minutes. Changes you make take effect automatically.

## Schedule Entry Format

```yaml
schedules:
  - label: descriptive-name        # What this schedule does
    cron: "minute hour dom month dow"  # 5-field cron expression
    prompt: "The prompt text..."    # What gets sent to you when it fires
    paused: false                   # Set to true to temporarily disable
    freshSession: false             # Set to true to start a clean session
```

## Adding a New Schedule

If Ian asks you to do something on a recurring basis, add a schedule entry to your YAML config. Example — checking market data every weekday at 7 AM:

```yaml
  - label: morning-market-check
    cron: "0 7 * * 1-5"
    prompt: "Check overnight market movements and update your intelligence brief."
    paused: false
    freshSession: false
```

The conductor picks it up within 5 minutes. No restart needed.

## Usage Limits and Peak Hours

Claude Code has a shared usage budget. All agents and personal usage draw from the same pool. Be aware of these constraints when scheduling:

**5-hour rolling session limit.** Starts from your first message, resets 5 hours later. Shared across Claude.ai, Claude Desktop, AND Claude Code — all agents plus Ian's personal usage. This is the binding constraint for sustained multi-agent operation.

**Weekly cap.** 7-day rolling window tied to the account. Not a fixed calendar reset.

**Peak-hour throttling.** Weekdays 5-11 AM PT (6 AM - 12 PM MDT). The 5-hour window drains FASTER during peak hours. Same work costs more budget during peak.

### Scheduling Guidelines

- **Target non-peak windows** for any scheduled work. Best windows:
  - Evening: 8-11 PM MDT (7-10 PM PT)
  - Early morning: 3-6 AM MDT (2-5 AM PT)
- **Avoid 6 AM - 12 PM MDT** for scheduled operations. This is peak throttling. Exception: Stamper's morning brief is intentionally in this window because its function (briefing Ian when he starts his day) requires it.
- **Keep scheduled operations short.** Sleep and caffeinate rituals should complete in 5-15 minutes. Don't add expensive operations (multi-hour research passes, large experiments) to scheduled crons without considering budget impact.
- **Stagger by at least 10 minutes** from other agents' schedules. Check the existing schedule grid before picking a time slot.
- **Prefer fewer, focused cron jobs** over many small ones. Each cron job starts a session that consumes budget. Three well-timed daily operations are better than twelve micro-checks.

## Pausing Schedules

Before long-running operations (multi-hour experiments, extended research sessions), pause your sleep schedule so it doesn't interrupt:

1. Edit your YAML config
2. Set `paused: true` on the relevant schedule
3. When done, set `paused: false`

The conductor also skips firing if you're actively working, so pausing is only needed for planned suppression.

## Removing a Schedule

Delete the entry from your YAML config. The conductor drops it on the next reload.

## Cron Syntax Quick Reference

```
*       = every value
1-5     = range (Monday through Friday)
1,3,5   = list (Mon, Wed, Fri)
*/5     = every 5th value
0-7     = day-of-week (0 and 7 both = Sunday)
```

## Ad-Hoc Ritual Tasks

If Ian asks you to add something to your morning routine, add it to `knowledge/caffeinate-additions.md` in your repo. Your scheduled caffeinate checks this file and executes anything listed. Same for `knowledge/sleep-additions.md`.

## What the Conductor Handles

- Fires your schedules at the right time
- Skips if you're already active (no interruption)
- Starts fresh sessions for caffeinate (clean context)
- Monitors rate limits and pauses all agents if budget is low
