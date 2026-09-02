# ERH Guardian Agent

A values-aligned AI agent built on the **AWS Strands Agents SDK** (Amazon Bedrock) whose
every consequential action is scored by the **Ethical Riemann Hypothesis (ERH) engine**
before it executes — with a human-in-the-loop gate when risk exceeds the user's threshold.

Built for the [Agents for Humans hackathon](https://agentsforhumans.devpost.com/)
(Professional Agents track).

## Why

Agents need *measurable* ethics, not vibes. The ERH engine treats critical misjudgments
as "ethical primes" and checks whether their accumulation stays under a Riemann-style
bound `|E(x)| ≤ C·x^(0.5+ε)`. A fitted growth exponent α ≈ 0.5 means the judgment system
is healthy; α → 1 means systematic failure. ERH Guardian puts that verdict — a 0–100
`risk_score`, a pass/fail `erh_satisfied`, and the exponent α — in front of every
consequential agent action, and pauses for human approval when the risk is too high.

Demo scenario: an IT/security assistant that audits AWS IAM grants for least-privilege
divergence (tagged with MITRE ATT&CK behavioral indicators) and proposes remediations.
Every remediation is ERH-scored and gated.

## Architecture

```mermaid
flowchart LR
    U[User / CLI / UI] <--> A[Strands Agent<br/>Bedrock Claude]
    A --> T1["@tool score_text"]
    A --> T2["@tool erh_evaluate_actions"]
    A --> T3["@tool audit_iam_grants"]
    A --> T4["@tool apply_iam_remediation<br/>(consequential — gated)"]
    G[GuardianGate hook<br/>BeforeToolCallEvent] -. "ERH score > threshold?<br/>cancel + ask human" .-> T4
    T1 & T2 & T3 --> E["ERH engine<br/>erh_engine.evaluate()"]
    P[(Value-alignment profile<br/>risk threshold · boundaries)] --> G
```

- **Agent**: Strands `Agent` with `BedrockModel` (Claude on Amazon Bedrock).
- **Tools**: thin `@tool` wrappers over the ERH engine's pure `evaluate()` contract.
- **GuardianGate**: a Strands `HookProvider` on `BeforeToolCallEvent` that scores the
  proposed action and uses `cancel_tool` to block it pending human approval.
- **Profile**: a validated value-alignment profile (risk threshold, protected topics,
  auto-approve list) that conditions every gate decision.

## Setup

Requires Python 3.10+, an AWS account with Bedrock model access (Claude), and AWS
credentials configured (`aws configure` or environment variables).

```bash
# from the Ethic-Latex repository root
python -m venv .venv && source .venv/bin/activate
pip install numpy scipy networkx fastapi requests pydantic   # ERH engine deps
pip install -e hackathon/erh-guardian-agent[dev]

# run the interactive guardian (needs Bedrock access)
erh-guardian chat

# run the offline demo scenario (no AWS calls; fixtures only)
erh-guardian demo

# tests
pytest hackathon/erh-guardian-agent/tests -q
```

Optional environment variables:

- `AWS_REGION` (default `us-west-2`)
- `ERH_GUARDIAN_MODEL` (default `global.anthropic.claude-sonnet-4-6`)
- `ERH_GUARDIAN_PROFILE` — path to a value-alignment profile JSON

## Pre-existing code disclosure

Per the hackathon rules, this project was newly created during the submission period
and **discloses** its use of the pre-existing open-source ERH engine
([dennislee928/Ethic-Latex](https://github.com/dennislee928/Ethic-Latex), MIT):
`erh_engine` / `erh_core` provide the ethical-scoring mathematics; everything under
`hackathon/erh-guardian-agent/` (the Strands agent, tools, HITL gate, CLI, UI) is new.

## License

MIT — see [LICENSE](./LICENSE).
