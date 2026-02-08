# Sub-Agent Patterns Skill

Comprehensive guide to sub-agents in Claude Code: built-in agents, custom agent creation, configuration, and delegation patterns.

## Auto-Trigger Keywords

This skill should be suggested when the user mentions:

**Sub-Agent Concepts:**
- "sub-agent", "sub-agents", "subagent", "subagents"
- "parallel agents", "multiple agents"
- "Task tool", "launch agents"
- "delegate tasks", "delegation"

**Built-in Agents:**
- "Explore agent", "explore subagent"
- "Plan agent", "plan subagent"
- "general-purpose agent"
- "thoroughness level", "quick/medium/thorough"

**Custom Agents:**
- ".claude/agents"
- "~/.claude/agents"
- "/agents command"
- "create agent", "custom agent"
- "--agents flag"

**Configuration:**
- "agent tools", "agent model"
- "permissionMode", "agent permissions"
- "agent skills", "agent hooks"
- "resumable agent", "resume agent"
- "disable agent", "Task(Explore)"

**Bulk Operations:**
- "bulk operations", "batch processing"
- "audit all", "update all", "check all"
- "swarm", "multi-agent"

**Errors:**
- "agent context", "agent timeout"
- "agent not responding"

## What This Skill Covers

1. **Built-in Sub-Agents** - Explore (Haiku, read-only), Plan (Sonnet, plan mode), General-purpose (Sonnet, all tools)
2. **Custom Agent Creation** - File format, YAML frontmatter, .claude/agents/ locations
3. **Configuration Fields** - name, description, tools, model, permissionMode, skills, hooks
4. **Model Selection** - sonnet, opus, haiku, inherit
5. **/agents Command** - Interactive agent management
6. **CLI Configuration** - `--agents '{...}'` flag
7. **Resumable Agents** - Continue previous conversations with agentId
8. **Disabling Agents** - Task(AgentName) permission rules
9. **Delegation Patterns** - The "repetitive + judgment" sweet spot
10. **Prompt Templates** - 5-step structure for audits, updates, research
11. **Batch Sizing** - 5-8 items per agent, 2-4 agents parallel
12. **Commit Strategy** - Agents edit, human commits

## Quick Example

### Built-in Explore Agent
```
User: Where are errors handled?
Claude: [Invokes Explore with "medium" thoroughness]
       → Returns: src/services/process.ts:712
```

### Custom Agent File (.claude/agents/code-reviewer.md)
```yaml
---
name: code-reviewer
description: Expert code reviewer. Use proactively after code changes.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer...
```

### Delegation Prompt Template
```markdown
For each [item]:
1. Read [source file]
2. Verify with [external check]
3. Check [authoritative source]
4. Evaluate/score
5. FIX issues found  ← Key instruction

Items: [list of 5-8 items]
```

## When NOT to Use Sub-Agents

- Single complex task (do it yourself)
- Simple find-replace (use scripts)
- Tasks with dependencies between items
- Creative/subjective decisions

## Production Tested

- Skill audits: 68 skills across 10 tiers (parallel batches)
- Description optimization: 58 skills in ~3 minutes
- Multi-site updates: 12 sites with consistent changes

## Related Skills

- `project-planning` - For planning complex multi-phase work
- `project-workflow` - For session management and handoffs

## References

- [Official Sub-Agents Documentation](https://code.claude.com/docs/en/sub-agents)
- [Tools Documentation](https://code.claude.com/docs/en/tools)
- [Hooks Documentation](https://code.claude.com/docs/en/hooks)
