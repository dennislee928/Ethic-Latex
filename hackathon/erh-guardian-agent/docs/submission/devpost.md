# Devpost submission draft — ERH Guardian

> Track: **Professional Agents** · Target submit date: **Sep 13, 2026**

## Tagline (≤200 chars)

> Every consequential action this Strands agent takes is scored by the Ethical
> Riemann Hypothesis engine — and gated by a human when risk crosses *your*
> threshold. Measurable ethics, not vibes.

(198 chars)

## Built with

`strands-agents` · `amazon-bedrock` · `python` · `mcp` · `cloudflare-workers` · `d1` · `drizzle` · `react` · `vite`

## Links to fill at submit time

- GitHub repo: https://github.com/dennislee928/erh-guardian-agent
- Video: `____________________`
- Live transparency panel: `____________________`
- builder.aws.com post: `____________________`
- AWS Builder ID email: `____________________`

---

## Long description

### What it does

ERH Guardian is a values-aligned professional agent for IT and security work.
Its defining behavior is **score before act**: before recommending or executing
anything consequential, it evaluates the action with the Ethical Riemann
Hypothesis (ERH) engine and surfaces the numbers — a 0–100 risk score, whether
the ERH bound holds, and the error-growth exponent α. Consequential tools pass
through the **GuardianGate**: when the risk exceeds the user's threshold, or the
action touches one of the user's protected topics, the tool call is cancelled
and a human must approve it. Every decision — auto-approved, human-approved, or
blocked — is logged to an auditable, public transparency panel.

### The problem

Agents are getting write access to production systems, and "the model seemed
aligned" is not an audit trail. Teams need three things current agents don't
give them: (1) a *quantitative* pre-action risk measure, (2) a hard,
user-defined boundary the agent cannot talk itself past, and (3) a tamper-proof
log a security reviewer can read after the fact. ERH Guardian is a working
pattern for all three.

### How ERH measures ethics

The ERH engine (pre-existing open-source work, disclosed below) treats ethical
misjudgments like error terms in an analytic bound. Each evaluated action gets
an ethical value in [-1, 1] and a complexity weight; severe misjudgments —
"ethical primes" — dominate the cumulative error J(x). The engine estimates the
growth exponent α of |J(x)|: a healthy decision stream stays near α ≈ 0.5
(errors cancel like random noise), while α drifting toward 1 means *systematic*
misjudgment. The verdict exposes `risk_score`, `erh_satisfied`,
`estimated_exponent`, the primes, and MITRE ATT&CK indicators for IAM findings.
One deliberate scoring subtlety: refusing a harmless request is itself scored
as a misjudgment (over-refusal clamps the score negative), so the bound can't
be gamed by refusing everything.

### Strands depth

- Four `@tool` wrappers over the engine's pure `evaluate()` contract:
  `score_text`, `erh_evaluate_actions`, `audit_iam_grants`, and the gated
  `apply_iam_remediation`.
- **GuardianGate** is a Strands `HookProvider` on `BeforeToolCallEvent`: it
  scores the proposed tool input, checks the user's value-alignment profile
  (risk threshold, protected topics, auto-approve list), and uses
  `cancel_tool` to block pending human approval. The model literally cannot
  execute past the gate — the boundary is enforced in the hook, not in the
  prompt.
- The agent discovers four more tools at runtime over **streamable-HTTP MCP**
  (`get_profile`, `update_profile`, `log_decision`, `list_decisions`) from a
  Cloudflare Worker, authenticated with a bearer token.
- Model: Claude on **Amazon Bedrock** (`global.anthropic.claude-sonnet-4-6`,
  us-west-2).

### Architecture

Strands agent (Python, Bedrock) ⇄ MCP worker on Cloudflare (Durable Object +
D1 via Drizzle) ⇄ React/Vite transparency panel (Cloudflare Pages) reading the
worker's public read-only API. The write surface (`/mcp`, `/sse`) is
bearer-token protected; the audit feed is deliberately public — transparency is
the product. Full diagram in the repo: `docs/architecture.svg`.

### What's next

Bedrock AgentCore Runtime deployment; richer HITL approval UI (approve / deny /
adjust threshold from the panel); OAuth on the MCP surface; per-team value
profiles.

### Pre-existing code disclosure

This project was newly created during the submission period. It **uses and
discloses** the pre-existing open-source ERH engine
([dennislee928/Ethic-Latex](https://github.com/dennislee928/Ethic-Latex), MIT)
as a scoring library, pinned as a versioned dependency in `pyproject.toml`.
Engine improvements made during the hackathon (Bedrock provider, over-refusal
scoring fix) were contributed back upstream in
[Ethic-Latex PR #95](https://github.com/dennislee928/Ethic-Latex/pull/95).
Everything in this repository — the Strands agent, tools, GuardianGate, CLI,
MCP worker, and transparency panel — is new work.
