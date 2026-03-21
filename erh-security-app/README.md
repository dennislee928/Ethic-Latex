## ERH-on-Security Proof-of-Concept

This repository hosts a small end-to-end prototype that maps DevSecOps data
(e.g. GitLab merge requests and security scans) into the Ethical Riemann
Hypothesis (ERH) framework.

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

Configure the backend URL via `NEXT_PUBLIC_API_BASE` if it is not running on
`http://localhost:8000`.


