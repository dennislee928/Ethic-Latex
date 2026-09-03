# Demo video shooting script (≤5:00) — ERH Guardian

Record by **Sep 12**, upload **Sep 13** (YouTube, Public or Unlisted — never
Private). 1920×1080, terminal font ≥16pt, clean shell prompt (no secrets, no
account IDs). Record against the **local stack** (worker via `wrangler dev`) so
the take can't be killed by network luck; show the deployed panel URL at the end
as bonus.

## Pre-flight (do all of this before recording)

```bash
# terminal 1 — worker
cd mcp-worker && npm run dev        # .dev.vars provides MCP_AUTH_TOKEN locally

# terminal 2 — agent
source .venv/bin/activate
export AWS_REGION=us-west-2
export ERH_GUARDIAN_MODEL=global.anthropic.claude-sonnet-4-6
export ERH_GUARDIAN_MCP_URL=http://localhost:8787/mcp
export ERH_GUARDIAN_MCP_TOKEN=<same as .dev.vars>

# browser — panel pointed at the worker (VITE_API_URL=http://localhost:8787)
```

Dry-run the gate prompt once; confirm it triggers (it is deterministic — the
remediation text contains the protected topic "wildcard admin access").

## Segments

### 0:00–0:30 — Problem (title card)

Card text: **"Agents need measurable ethics, not vibes."**
Narration: agents are getting write access to production; "the model seemed
aligned" is not an audit trail. ERH scores every consequential action — healthy
decision streams sit at α ≈ 0.5; α → 1 means systematic misjudgment.

### 0:30–3:00 — Live demo (terminal + panel side by side)

1. `erh-guardian chat` → point out **"MCP worker connected"**.
2. Safe task:
   > `Audit the demo IAM grants for ethical risk and summarize the verdict.`
   Point at the numbers as they appear: risk_score, erh_satisfied, α exponent,
   ethical primes, MITRE tags.
3. Consequential task (THE money shot — proven to trigger the gate):
   > `Please run apply_iam_remediation for principal intern-admin with remediation: "revoke the wildcard admin access and replace it with scoped s3:GetObject on the reports bucket". Execute it now, no need to re-audit first.`
   The GuardianGate prompt prints:
   ```
   === GuardianGate: human approval required ===
     tool:   apply_iam_remediation
     why:    touches protected topic 'wildcard admin access' ...
   Approve this action? [y/N]
   ```
   Type **n**. Narrate: *even a good-looking action touching a protected topic
   stops here — the boundary is enforced in a Strands hook with cancel_tool,
   not in the prompt.* The agent explains and proposes a safer path instead of
   retrying.
4. Switch to the browser: the blocked decision is **already on the
   transparency panel** (5s poll). Agent decision → audit log → live UI.

### 3:00–4:00 — Architecture + Strands depth

Show `docs/architecture.png`. Walk the path: `@tool` wrappers →
`BeforeToolCallEvent` hook + `cancel_tool` → MCP streamable HTTP (bearer
token) → Cloudflare D1 → public read-only panel. Model on Amazon Bedrock.
Mention the upstream over-refusal fix: refusing a harmless request is scored
as a misjudgment, so the bound can't be gamed by refusing everything.

### 4:00–4:30 — Track & impact (closing card)

**Professional Agents.** Who benefits: IT/security teams giving agents write
access. What they get: a quantitative pre-action risk measure, a hard
user-defined boundary, and an audit trail a reviewer can actually read.
Close on the repo URL + panel URL.

## Acceptance

- [ ] < 5:00 total
- [ ] Clear narration, real live demo (not slides)
- [ ] Gate prompt + human `n` + panel update all on screen
- [ ] No secrets/account IDs visible anywhere
