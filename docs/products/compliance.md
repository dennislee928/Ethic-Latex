# Compliance & Framework Mapping

The ERH products are positioned against established AI-risk and cloud-security
frameworks. This is positioning guidance, not a certification.

## NIST AI RMF (Measure / Manage)

- **Measure** — `erh_engine` quantifies misjudgment-error growth (`risk_score`,
  `estimated_exponent`, `violation_rate`) as a continuous, auditable metric of an
  AI system's logical/ethical health.
- **Manage** — the CI/CD gate and runtime AI firewall convert that measurement
  into enforcement (block/fail) across the DevSecOps lifecycle.

## Cloud Security Alliance (CSA) — LLM security

CSA highlights data-leakage and access-control risk when adopting LLMs at scale.
Deploying ERH at the **API gateway layer** (the runtime AI firewall) is the
architecturally appropriate enforcement point, consistent with that guidance.

## MITRE ATT&CK — IOB over IOC

The IAM/CSPM and UEBA adapters emit **indicators of behavior (IOB)** rather than
static indicators of compromise (IOC):

- IAM over-grants → `T1098` (Account Manipulation), `T1530` (Data from Cloud
  Storage), `T1078.004` (Valid Accounts: Cloud Accounts) in `context.mitre_iob`.
- UEBA drift → behavioral deviation trajectories feeding SOC decision support.

This aligns with modern heuristic defense that scores *behavioral divergence*
instead of matching known-bad signatures.
