## ERH-on-Security Proof-of-Concept

This repository hosts a small end-to-end prototype that maps DevSecOps data
(e.g. GitLab merge requests and security scans) into the Ethical Riemann
Hypothesis (ERH) framework.

### Current Status

Status date: `2026-04-12`

The currently revalidated path in this subproject is:

- `backend/`: FastAPI backend with regression coverage
- `frontend/`: Next.js dashboard with passing `typecheck`, `build`, and `lint`

`frontend-vite/` remains in the tree as an alternate implementation, but it is
not part of the latest verified surface.

### Structure

- `backend/`: FastAPI application, database models, ingestion, and ERH analysis.
- `frontend/`: Next.js dashboard for visualising ERH metrics.
- `frontend-vite/`: React + Vite dashboard (alternative).

### Backend (FastAPI)

From `backend/`:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

To run the verified backend tests:

```bash
cd backend
python -m pytest tests -q
```

Key endpoints:

- `POST /ingestion/run?mode=mock` – generate synthetic DevSecOps data.
- `POST /ingestion/huggingface` – ingest HuggingFace ethics datasets (ethics_commonsense, social_i_qa, moral_stories).
- `POST /ingestion/aita` – ingest Reddit r/AmItheAsshole data (Firecrawl or stub).
- `GET /analysis/summary` – high-level ERH summary.
- `GET /analysis/curves` – Pi(x) and E(x) curves.
- `GET /analysis/heatmap` – complexity vs average Δ heatmap.

### Frontend (Next.js)

From `frontend/`:

```bash
npm install
npm run dev
```

To run the verified frontend checks:

```bash
cd frontend
npm run typecheck
npm run build
npm run lint
```

Configure the backend URL via `NEXT_PUBLIC_API_BASE` if it is not running on
`http://localhost:8000`.

