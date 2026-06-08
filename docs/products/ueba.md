# UEBA Insider-Threat

Builds a per-user **behavioral convergence domain** from baseline events, then
measures how far later behavior deviates. A rising ERH error trajectory signals a
slow insider drift rather than isolated noise.

Adapter: `erh_engine/adapters/ueba.py`. Per event: `x` = situational complexity
(off-hours + sensitivity + volume anomaly), `V` = the user's normal pole,
`J` drops with deviation signals, `weight` = data sensitivity. Temporal drift can
be tracked with `erh_core/core/temporal_erh.py` + `MetaMonitor`.

## Use

```bash
PYTHONPATH=. ERH_MODE=rest python -m erh_engine.serve &
curl -s -X POST localhost:8000/v1/ueba/evaluate \
  -H 'Content-Type: application/json' \
  -d '{"events":[
        {"user":"a","hour":10,"bytes_downloaded":120,"is_baseline":true},
        {"user":"a","hour":11,"bytes_downloaded":90,"is_baseline":true},
        {"user":"a","hour":2,"bytes_downloaded":9000,"sensitive":true}
      ]}'
```

## Dashboard

The Next.js security frontend exposes a `/ueba` route
(`erh-security-app/frontend/src/pages/ueba.tsx`) that posts events to the engine
and renders the behavioral-deviation trajectory (`E(x)`) plus a risk verdict.
Set `NEXT_PUBLIC_ERH_ENGINE_BASE` to the engine URL.
