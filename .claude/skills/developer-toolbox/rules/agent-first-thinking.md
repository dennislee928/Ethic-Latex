---
description: Behavioral interrupt - consider agents before manual work
alwaysApply: true
---

# Agent-First Thinking

## The Rule

**Before doing repetitive or multi-step manual work, ask: "Could agents do this?"**

This is a behavioral interrupt, not a suggestion.

## Triggers (STOP When You Notice These)

| If you're about to... | STOP and consider... |
|-----------------------|----------------------|
| `grep` or `glob` 3+ times | Explore agent |
| Read 5+ files to understand something | Explore agent |
| Do same edit across multiple files | Parallel agents |
| Audit/verify multiple items | Parallel swarm |
| Research multiple options | Parallel research |

## The Inversion

❌ Wrong mental model: "I'll do this manually unless it's big enough for agents"

✅ Right mental model: "I'll use agents unless there's a reason not to"

## Quick Decision

```
Is this a single, one-off action?
  YES → Do it manually
  NO  → Use agents
```

## Why This Matters

Manual grep/read loops waste tokens and time. Each back-and-forth costs ~500 tokens. An Explore agent does it in one call with better results.

Measured: 70 skill audits took 3 minutes with agents vs ~70 minutes manually.

## When Agents DON'T Fit

Only skip agents when:
- **Single, one-off action** - One file, one search, one edit
- **Real-time creative direction** - Needs constant human input
- **Cross-item dependencies** - Items depend on each other's results
