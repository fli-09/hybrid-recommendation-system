# Deployment Guide

## Docker Setup

Build the image from the repository root:

```bash
docker build -t hybrid-recommendation-system .
```

Run the API on port 8000:

```bash
docker run --rm -p 8000:8000 hybrid-recommendation-system
```

The container starts the API with:

```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000
```

## Compose Deployment

Docker Compose mounts artifacts, configuration, and data as read-only paths and includes an HTTP health check.

```bash
docker-compose up --build
```

Verify readiness at `http://localhost:8000/api/v1/health`.

## API Deployment Considerations

- Configure `ALLOWED_ORIGINS` with the trusted frontend origins for the target environment.
- Configure `LOG_LEVEL` to control application logging.
- Put the service behind a TLS-terminating reverse proxy or managed ingress in production.
- Size memory for the loaded ALS factors and TF-IDF artifacts before selecting a host or container limit.

## Artifact Management

Inference requires the contents of `artifacts/` and the mapping files in `data/processed/mappings/`. These files must be versioned and deployed as a compatible set with the pinned Python dependencies, especially `scikit-learn==1.6.1` for serialized TF-IDF artifacts.

For larger environments, store artifacts in versioned object storage or a model registry and mount or fetch them during deployment. Do not replace artifacts independently of their matching configuration and dependency versions.
