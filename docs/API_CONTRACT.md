# ERH API Contract

This document defines the API contract between the Python backend and JavaScript/TypeScript clients.

## Version

**Current API Version:** `v1.0.0`

## Base URL

- Default: `http://localhost:8000`
- Production: TBD

## Endpoints

### Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

**Status Codes:**
- `200 OK`: Service is healthy
- `500 Internal Server Error`: Service is unavailable

**Client Implementation:**
- Python: `ERHRemoteClient.health() -> bool`
- JavaScript: `ERHClient.healthCheck() -> Promise<boolean>`

---

### Run Simulation

**Endpoint:** `POST /simulate`

**Request Body:**
```json
{
  "num_actions": 1000,
  "complexity_dist": "zipf"
}
```

**Parameters:**
- `num_actions` (integer, optional, default: 1000): Number of actions to simulate
  - Range: 100 - 10000
  - Validation: Must be positive integer
- `complexity_dist` (string, optional, default: "zipf"): Complexity distribution
  - Allowed values: `"zipf"`, `"uniform"`, `"power_law"`
  - Validation: Must be one of the allowed values

**Response:**
```json
{
  "mistake_rate": 0.234,
  "ethical_primes_count": 45,
  "analysis": {
    "estimated_exponent": 0.412,
    "alpha_ci_low": 0.389,
    "alpha_ci_high": 0.435,
    "erh_satisfied": true,
    "r_squared": 0.876,
    "growth_rate": "sublinear_slow"
  },
  "config": {
    "num_actions": 1000,
    "complexity_dist": "zipf",
    "tau": 0.3
  }
}
```

**Response Fields:**
- `mistake_rate` (float): Proportion of misjudgments (0.0 - 1.0)
- `ethical_primes_count` (integer): Number of ethical primes identified
- `analysis.estimated_exponent` (float): Growth exponent α
- `analysis.alpha_ci_low` (float): Lower bound of 95% CI for α
- `analysis.alpha_ci_high` (float): Upper bound of 95% CI for α
- `analysis.erh_satisfied` (boolean): Whether ERH-style bound is satisfied
- `analysis.r_squared` (float): Goodness of fit (0.0 - 1.0)
- `analysis.growth_rate` (string): Qualitative growth category
- `config`: Echo of request parameters

**Status Codes:**
- `200 OK`: Simulation completed successfully
- `400 Bad Request`: Invalid parameters
- `500 Internal Server Error`: Simulation failed

**Error Response:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

**Client Implementation:**
- Python: `ERHRemoteClient.run_simulation(num_actions, complexity_dist) -> Dict`
- JavaScript: `ERHClient.runSimulation(numActions, complexityDist) -> Promise<Object>`

---

## Data Types

### Complexity Distribution
- `"zipf"`: Zipf distribution (many simple, few complex)
- `"uniform"`: Uniform distribution
- `"power_law"`: Power law distribution

### Growth Rate Categories
- `"sublinear_slow"`: α < 0.4 (better than ERH)
- `"square_root"`: 0.4 ≤ α < 0.6 (consistent with ERH)
- `"sublinear_fast"`: 0.6 ≤ α < 0.9
- `"linear"`: 0.9 ≤ α < 1.1
- `"superlinear"`: α ≥ 1.1 (problematic)

---

## Versioning Strategy

- **Major version** (v1, v2): Breaking changes to API structure
- **Minor version** (v1.0, v1.1): New endpoints or optional fields
- **Patch version** (v1.0.0, v1.0.1): Bug fixes, no API changes

## Backward Compatibility

- New optional fields may be added without version bump
- Existing fields will not be removed without major version bump
- Clients should ignore unknown fields in responses

## Client Requirements

### Python Client
- Must validate `num_actions` range (100-10000)
- Must validate `complexity_dist` against allowed values
- Must handle network errors gracefully
- Must parse JSON responses correctly

### JavaScript Client
- Must validate `numActions` range (100-10000)
- Must validate `complexityDist` against allowed values
- Must handle fetch errors and network failures
- Must parse JSON responses correctly
- Should provide TypeScript type definitions

---

## Testing

Both clients should be tested against:
1. Valid requests with all parameter combinations
2. Invalid parameter values (out of range, wrong type)
3. Network failures and timeouts
4. Malformed JSON responses
5. Server errors (500 status codes)

---

## Changelog

### v1.0.0 (2024-12-18)
- Initial API contract
- Health check endpoint
- Simulation endpoint with basic parameters

