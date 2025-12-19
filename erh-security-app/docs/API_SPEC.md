# ERH-on-Security API Specification

Base URL (local development):

- `http://localhost:8000`

## Health

### `GET /health/`

Returns:

- `status`: `"ok"`
- `app_name`: application name

## Ingestion

### `POST /ingestion/run`

Query parameters:

- `mode` (string, default `"mock"`): `"mock"` or `"gitlab"`.
- `updated_after` (optional, ISO-8601 string): filter recent MRs.

Responses:

- `200 OK` (mock mode):
  - `mode`: `"mock"`
  - `actions_created`: integer
  - `judgments_created`: integer
- `200 OK` (gitlab mode):
  - `mode`: `"gitlab"`
  - `actions_processed`: integer

## Analysis

### `GET /analysis/summary`

Query parameters:

- `judge_type`: `"PIPELINE" | "HUMAN" | "COMBINED"` (default `"COMBINED"`).

Response:

- `judge_type`: judge type string
- `num_samples`: integer
- `num_primes`: integer
- `estimated_alpha`: number or `null`
- `r_squared`: number or `null`

### `GET /analysis/curves`

Query parameters:

- `judge_type` as above.

Response:

- `pi_curve`: array of `{ "x": number, "y": number }`
- `error_curve`: array of `{ "x": number, "y": number }`

### `GET /analysis/heatmap`

Query parameters:

- `judge_type` as above.
- `bins` (integer, optional, default `10`).

Response:

- `judge_type`: judge type string
- `cells`: array of:
  - `complexity_bin`: number (bin centre)
  - `delta_mean`: number (average Δ in bin)
  - `count`: integer (samples in bin)


