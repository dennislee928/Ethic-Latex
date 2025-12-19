# Infrastructure Files

This directory contains Dockerfiles and infrastructure configuration files for deploying the application.

## Files

- `Dockerfile.fastapi` - Production Dockerfile for the FastAPI backend

## Building the FastAPI Backend

From the repository root:

```bash
docker build -f infra/Dockerfile.fastapi -t ethic-latex-api .
```

## Running the Container

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:password@host:5432/dbname \
  -e PORT=8000 \
  ethic-latex-api
```

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string (required)
- `PORT` - Port to run the server on (default: 8000)
- `LOG_LEVEL` - Logging level (default: INFO)
- `GITLAB_BASE_URL` - GitLab base URL (optional)
- `GITLAB_TOKEN` - GitLab access token (optional)

## Cloud Platform Deployment

### Render

Use this Dockerfile with Render's Docker deployment option.

### Railway

Use this Dockerfile with Railway's Dockerfile deployment.

### Other Platforms

The Dockerfile is designed to work with any Docker-compatible platform. Make sure to:
1. Set the `DATABASE_URL` environment variable
2. Configure the `PORT` environment variable (if your platform requires it)
3. Ensure the build context is set to the repository root

