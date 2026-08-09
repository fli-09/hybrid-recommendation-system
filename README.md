# Hybrid Recommendation System

## Overview

A production-ready hybrid recommendation service built with Python and FastAPI. The system combines collaborative filtering (ALS) and content-based filtering (TF-IDF similarity) to deliver personalized e-commerce recommendations.

Key capabilities:
- Personalized recommendations for known users
- Content-based similarity recommendations for cold-start cases
- Hybrid score fusion across ALS and content signals
- REST API served by FastAPI
- Docker and Docker Compose deployment support

## Features

- ALS-based collaborative filtering
- TF-IDF content similarity ranking
- Weighted hybrid model with configurable weights
- Popular-item fallback for unknown users
- FastAPI endpoints for health checks, user recommendations, hybrid scoring, and text search
- Artifact-driven inference with serialized model assets

## Repository Structure

```text
Hybrid-Recommendation-System/
├── api/                     # FastAPI app, routes, schemas
├── artifacts/               # Serialized models and inference assets
├── configs/                 # Model and deployment configuration
├── data/                    # Raw and processed dataset files
├── deployment/              # Deployment-related configs and frontend assets
├── docs/                    # Architecture and deployment documentation
├── evaluation/              # Offline evaluation metrics and reports
├── notebooks/               # Analysis and experimentation notebooks
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Compose deployment for the API
├── Dockerfile               # Container image build definition
└── README.md                # Project overview and setup
```

## Getting Started

### Prerequisites

- Python 3.8+ (recommended)
- Git
- Docker (optional, for container deployment)
- A virtual environment tool such as `venv`

### Install dependencies

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run locally with Uvicorn

Start the API from the repo root:

```powershell
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

Once started, the service is available at:
- `http://localhost:8000/`
- `http://localhost:8000/api/v1/`
- `http://localhost:8000/docs`

### Run with Docker Compose

Build and start the API container:

```powershell
docker-compose up --build
```

The API will listen on port `8000`.

## API Reference

### Health Check

- `GET /api/v1/health`

Response example:

```json
{
  "status": "healthy",
  "models_loaded": true
}
```

### User Recommendation (Hybrid)

- `GET /api/v1/recommend/{user_id}`
- Query parameters:
  - `top_n` (optional, default `10`)

Example:

```bash
curl "http://localhost:8000/api/v1/recommend/42?top_n=10"
```

### Hybrid Recommendation by POST

- `POST /api/v1/recommend/hybrid`
- `Content-Type: application/json`

Request body:

```json
{
  "user_id": 42,
  "top_n": 10,
  "weights": {
    "als": 0.6,
    "content": 0.4
  }
}
```

### Alias POST endpoint

- `POST /api/v1/predict`
- Same request body as `/recommend/hybrid`

### ALS-only Recommendations

- `POST /api/v1/recommend/als`

### Content-only Recommendations

- `POST /api/v1/recommend/content`

### Text Search Recommendations

- `POST /api/v1/recommend/search`

Request body:

```json
{
  "query": "wireless headphones",
  "top_n": 10
}
```

## API Response Schema

All recommendation responses include:
- `user_id` (when applicable)
- `model_used`
- `recommendations` list
- `metadata` (optional)

Each recommended item contains:
- `item_id`
- `score`
- `source`
- optional product metadata fields such as `product_name`, `category`, `brand`, `price`, `image_url`, and `description`

## Data and Artifacts

The service depends on serialized inference assets in `artifacts/` and mapping files under `data/processed/mappings/`.

Ensure the corresponding artifacts are available before starting the API. Mismatched or missing artifact files may prevent model loading.

## Deployment

### Docker

Build the container image:

```bash
docker build -t hybrid-recommendation-system .
```

Run it locally:

```bash
docker run --rm -p 8000:8000 hybrid-recommendation-system
```

### Docker Compose

Use the provided compose file to mount artifacts and configuration:

```bash
docker-compose up --build
```

The compose service includes a health check against `http://127.0.0.1:8000/api/v1/health`.

## Configuration

Environment variables supported by deployment:
- `LOG_LEVEL` – logging verbosity (`INFO`, `DEBUG`, etc.)
- `ALLOWED_ORIGINS` – comma-separated CORS origins
- `APP_HOST` – host binding for Uvicorn
- `APP_PORT` – service port

The app also reads deployment settings from `configs/deployment_config.yaml`.

## Development

### Run tests

From the repo root:

```powershell
pytest
```

### Recommended workflow

1. Activate the virtual environment
2. Install dependencies
3. Run tests after code changes
4. Use `uvicorn` for local API development

## Requirements

Core dependencies are listed in `requirements.txt` and include:
- `fastapi`
- `uvicorn`
- `pydantic`
- `numpy`
- `pandas`
- `scikit-learn`
- `scipy`
- `PyYAML`

## Notes

- The API entrypoint is `api/app.py`.
- The FastAPI router is mounted under `/api/v1`.
- The project supports both direct Python execution and Docker deployment.

## License

See the `LICENSE` file for license details.

Example:

```bash
curl "http://localhost:8000/api/v1/recommend/1150086?top_n=10"
```

Response:

```json
{
  "user_id":1150086,
  "model_used":"HybridRecommender",
  "recommendations":[
    {
      "item_id":143866,
      "score":0.5,
      "source":"Hybrid"
    },
    {
      "item_id":87413,
      "score":0.5,
      "source":"Hybrid"
    }
  ]
}
```

---

## ALS Recommendation

### Endpoint

```
POST /api/v1/recommend/als
```

Generates recommendations using collaborative filtering.

---

## Content Recommendation

### Endpoint

```
POST /api/v1/recommend/content
```

Uses:

- User interaction history when available
- ALS generated seed item when history is unavailable

---

# Running Locally

Clone repository:

```bash
git clone <repository-url>

cd Hybrid-Recommendation-System
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
pytest tests/
```

Start API:

```bash
uvicorn api.app:app --reload
```

---

# Docker Deployment

Build container:

```bash
docker compose build
```

Run service:

```bash
docker compose up -d
```

Check running container:

```bash
docker ps
```

Example output:

```
hybrid_recommendation_api
STATUS: healthy
PORT: 8000
```

API available at:

```
http://localhost:8000/docs
```

---

# Testing

The project includes automated tests covering:

- ALS predictor
- Content predictor
- Hybrid recommender
- API endpoints
- Model loading
- Cold-start handling
- Response schema validation


Current test status:

```
30 passed
```

---

# Future Improvements

- React-based recommendation dashboard
- Real-time recommendation updates
- Online learning from user interactions
- Session-based recommendation models
- Deep learning ranking models
- Cloud deployment with monitoring and autoscaling