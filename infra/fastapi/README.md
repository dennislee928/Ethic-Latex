# FastAPI Backend Dockerfile

This Dockerfile builds the FastAPI backend for the Ethic-Latex project.

## Build Context Configuration

**IMPORTANT:** The build context MUST be set to the repository root (`.`), NOT to `infra/fastapi/`.

## For Render Deployment

When deploying on Render:

1. **Root Directory**: Set to `.` (repository root)
2. **Dockerfile Path**: Set to `infra/fastapi/Dockerfile`
3. **Build Command**: Leave empty (Docker handles it)
4. **Start Command**: Leave empty (defined in Dockerfile CMD)

### Render Configuration Steps:

1. Go to your Render dashboard
2. Create a new "Web Service"
3. Connect your GitHub repository
4. In the settings:
   - **Root Directory**: `.` (or leave empty if it defaults to root)
   - **Environment**: `Docker`
   - **Dockerfile Path**: `infra/fastapi/Dockerfile`
   - **Build Command**: (leave empty)
   - **Start Command**: (leave empty)

## For Local Build

From the repository root:

```bash
docker build -f infra/fastapi/Dockerfile -t ethic-latex-api .
```

## Environment Variables

Required environment variables:

- `DATABASE_URL` - PostgreSQL connection string (required)
  - Example: `postgresql://user:password@host:5432/dbname`

Optional environment variables:

- `PORT` - Port to run the server on (default: 8000)
- `LOG_LEVEL` - Logging level (default: INFO)
- `GITLAB_BASE_URL` - GitLab base URL (optional)
- `GITLAB_TOKEN` - GitLab access token (optional)

## Running Locally

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:password@host:5432/dbname \
  -e PORT=8000 \
  ethic-latex-api
```

## Troubleshooting

If you see errors like:
```
ERROR: failed to calculate checksum of ref ... "/erh-security-app/backend": not found
```

This means the build context is incorrect. Make sure:
1. You're building from the repository root
2. On Render, the Root Directory is set to `.` (repository root)
3. The Dockerfile Path is set to `infra/fastapi/Dockerfile`

