---
description: Patterns for effective sub-agent delegation - tool access principle, model selection, prompt templates, workflow patterns
alwaysApply: false
---

# Sub-Agent Delegation Patterns

Operational knowledge for effective sub-agent delegation in Claude Code.

---

## Tool Access Principle (CRITICAL)

**If an agent doesn't need Bash, don't give it Bash.**

| Agent needs to... | Give tools | Don't give |
|-------------------|------------|------------|
| Create files only | Read, Write, Edit, Glob, Grep | Bash |
| Run scripts/CLIs | Read, Write, Edit, Glob, Grep, Bash | — |
| Read/audit only | Read, Glob, Grep | Write, Edit, Bash |

**Why?** Models default to `cat > file << 'EOF'` heredocs instead of Write tool. Each bash command requires approval, causing dozens of prompts per agent run.

**Fix Bash approval spam:**
1. Remove Bash from tools list if not needed
2. Put critical instructions FIRST (right after frontmatter)
3. Remove contradictory instructions (don't mention bash if you want Write tool)

---

## Model Selection (Quality-First)

| Model | Best For |
|-------|----------|
| **Sonnet** | Most agents - content, files, code (default) |
| **Opus** | Creative work, quality-critical outputs |
| **Haiku** | Only script runners where quality doesn't matter |

**Why Sonnet default?** Testing showed Haiku produces wrong patterns, missing CSS, incorrect values. Sonnet gets it right first time.

---

## The Sweet Spot

**Best use case**: Tasks that are **repetitive but require judgment**.

Example: Auditing 70 skills manually = tedious. But each audit needs intelligence (check docs, compare versions, decide what to fix). Perfect for parallel agents with clear instructions.

**Not good for**: Simple tasks (just do them), highly creative tasks (need human direction), tasks requiring cross-file coordination (agents work independently).

---

## Effective Prompt Template

```
For each [item]:
1. Read [source file]
2. Verify with [external check - npm view, API call, etc.]
3. Check [authoritative source]
4. Score/evaluate
5. FIX issues found ← Critical instruction
```

**Key elements**:
- **"FIX issues found"** - Without this, agents only report. With it, they take action.
- **Exact file paths** - Prevents ambiguity and wrong-file edits
- **Output format template** - Ensures consistent, parseable reports
- **Batch size ~5 items** - Enough work to be efficient, not so much that failures cascade

---

## Workflow Pattern

```
1. ME: Launch 2-3 parallel agents with identical prompt, different item lists
2. AGENTS: Work in parallel (read → verify → check → edit → report)
3. AGENTS: Return structured reports (score, status, fixes applied, files modified)
4. ME: Review changes (git status, spot-check diffs)
5. ME: Commit in batches with meaningful changelog
6. ME: Push and update progress tracking
```

**Why agents don't commit**: Allows human review, batching, and clean commit history.

---

## Signs a Task Fits This Pattern

✅ Same steps repeated for many items
✅ Each item requires judgment (not just transformation)
✅ Items are independent (no cross-item dependencies)
✅ Clear success criteria (score, pass/fail, etc.)
✅ Authoritative source exists to verify against

❌ Items depend on each other's results
❌ Requires creative/subjective decisions
❌ Single complex task (use regular agent instead)
❌ Needs human input mid-process

---

## Real Example: Skill Audits

**Task**: Audit 70 skills for version accuracy and content correctness

**Prompt template**:
```
Deep audit these 5 skills. For each:
1. Read SKILL.md
2. Verify versions with npm view
3. Check official docs (use cloudflare-docs MCP or WebFetch)
4. Score 1-10
5. FIX issues found

Skills: [list of 5]
```

**Results**:
- 15 Cloudflare skills audited in ~3 minutes (3 parallel agents)
- 10 Frontend skills audited in ~2 minutes (2 parallel agents)
- Caught: outdated versions, wrong limits, missing features
- All fixed automatically by agents

---

**Last Updated**: 2026-01-14
