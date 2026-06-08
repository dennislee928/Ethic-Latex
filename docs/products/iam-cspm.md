# Cloud IAM Logic Audit / Zero-Trust CSPM

Quantifies how far IAM grants diverge from a least-privilege baseline and whether
over-permission **grows structurally** with policy complexity (logical privilege
escalation) — blocking high-risk configurations before they ship.

Adapter: `erh_engine/adapters/iam_cspm.py`. Per grant: `x` = breadth
(actions × resources × principals), `V` = least-privilege baseline, `J` = actual
granted scope, `weight` = asset criticality / internet exposure. Findings carry
MITRE ATT&CK IOB tags in `context.mitre_iob`.

## Use

```bash
PYTHONPATH=. ERH_MODE=rest python -m erh_engine.serve &
curl -s -X POST localhost:8000/v1/iam/audit \
  -H 'Content-Type: application/json' \
  -d @erh_engine/examples/iam_grants.json | jq '{risk_score, erh_satisfied, primes}'
```

The wildcard `*/*` grant on an internet-exposed critical asset surfaces as an
ethical prime with IOB tags `T1098`, `T1530`, `T1078.004`.

## Live AWS

`pull_aws_grants()` reads users/policies via boto3 when AWS credentials are
configured; feed the result to `grants_to_samples()` → `/v1/iam/audit`.
