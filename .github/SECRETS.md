# GitHub Secrets Configuration

This document describes the repository and workflow secrets used by GitHub Actions and deployment.

## Required Secrets (Repository / Environment)

### `IBM_QUANTUM_TOKEN`

- **Used by:** `quantum_tests.yml` (Cloud Quantum Judge job), `simulation/quantum/cloud.py`, quantum-worker in Docker Compose
- **Purpose:** Authenticate with IBM Quantum Platform for `CloudQuantumJudge` and batch quantum judgment runs
- **How to obtain:** [IBM Quantum Platform](https://quantum.ibm.com/) → Account → API token
- **Optional:** Workflows and workers run without it using `LocalQuantumJudge` (AerSimulator or NumPy fallback)

### `PYPI_TOKEN`

- **Used by:** `sdk_python.yml` (publish job)
- **Purpose:** Publish the `erh` package to PyPI when a version tag (e.g. `v1.0.0`) is pushed
- **How to obtain:** [PyPI](https://pypi.org/) → Account → API tokens → Add API token (scope: entire account or specific project)
- **Required:** Only if you publish to PyPI; otherwise the publish step is skipped when no tag is pushed

### `POSTGRES_PASSWORD`

- **Used by:** Docker Compose (`postgres` service), `erh-security-app` backend when `DATABASE_URL` is set
- **Purpose:** PostgreSQL database password for `erh_user` in development and production
- **Set:** In repository secrets for CI, or in `.env` for local `docker-compose`
- **Required:** For full stack (postgres, erh-backend); use a strong value in production

## Optional Secrets

### `COMPAS_DATA_URL`

- **Used by:** `simulation.yml` (real-data-preparation job)
- **Purpose:** URL to download COMPAS dataset (e.g. `compas-scores-two-years.csv`) when not using Git LFS
- **Format:** Full URL to a CSV file (HTTPS)
- **Optional:** Alpha comparison still runs with Adult Income and simulated data if COMPAS is missing

## Setting Secrets

1. **Repository:** Settings → Secrets and variables → Actions → New repository secret
2. **Environment (e.g. production):** Settings → Environments → [env name] → Environment secrets

## Local Development

Copy `.env.example` to `.env` and set values locally. Do not commit `.env`. Use:

- `IBM_QUANTUM_TOKEN` – optional, for CloudQuantumJudge
- `POSTGRES_PASSWORD` – for `docker-compose` postgres
- `REDIS_URL` – for quantum-worker and backend (default `redis://localhost:6379/0`)
- `COMPAS_DATA_URL` – only if you need COMPAS in CI and do not use Git LFS

## Summary

| Secret               | Required for CI | Required for Publish | Used in Docker |
|----------------------|-----------------|----------------------|----------------|
| `IBM_QUANTUM_TOKEN`  | No              | No                   | Yes (optional) |
| `PYPI_TOKEN`         | No              | Yes (on tag push)    | No             |
| `POSTGRES_PASSWORD`  | No              | No                   | Yes            |
| `COMPAS_DATA_URL`    | No              | No                   | No             |
