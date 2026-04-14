# Intelligence System

This directory contains intelligence briefs -- living documents that distill environmental scanning about your domain's landscape.

## How It Works

`/research` sessions scan the external world and produce/update intelligence briefs here. `/meditate` sessions consume these briefs to recalibrate beliefs. The action items file tracks proposed changes.

## Brief Template

Each brief follows this structure:

```markdown
# [Domain Area] Intelligence Brief

**Last updated:** YYYY-MM-DD

## Current Assessment
Narrative snapshot. Readable in under 2 minutes.

## Watch List
| What to Watch | Why It Matters | Change Signal |
|---|---|---|

## Updates

### YYYY-MM-DD
**Key findings:**
- Finding with source attribution

**What it means:**
- Implication or connection

**Questions raised:**
- Open questions for future research
```

## Action Items

`action-items.md` tracks proposed changes from research sessions:
- **Proposed** -- identified by research, not yet evaluated
- **Accepted** -- evaluated by meditation, approved for execution
- **Declined** -- evaluated and passed on (with reason)
- **Completed** -- done

Meditation evaluates proposals. Sessions execute accepted items.
