# 🚀 Kickstarter Campaign Advisor (KCA)

> **An AI-powered web application that predicts Kickstarter campaign success using Machine Learning and Vector Similarity Search.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-000000?style=flat&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)](https://docker.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?style=flat&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat&logo=redis&logoColor=white)](https://redis.io)
[![Celery](https://img.shields.io/badge/Celery-5.4-37814A?style=flat)](https://docs.celeryq.dev)
[![CatBoost](https://img.shields.io/badge/CatBoost-1.2-yellow?style=flat)](https://catboost.ai)

---

## 📖 Overview

**Kickstarter Campaign Advisor (KCA)** helps creators evaluate the potential success of their crowdfunding campaigns before launching. By analyzing over **300,000 historical Kickstarter campaigns**, the system uses a **CatBoost** classification model and **AI-powered Vector Search** to provide:

- 🎯 **Success probability score** for your campaign
- 🔍 **Similar past campaigns** as real-world references
- 💡 **Actionable insights** to improve campaign structure
- ⚡ **Asynchronous job queue** for non-blocking ML inference via Celery

---

## 🆕 Updates

### v2.0 — Async ML Pipeline & Model Upgrade

| # | Change | Detail |
|---|---|---|
| 1 | **Model upgrade** | Replaced XGBoost with **CatBoost v2** (`kca_classifier_v2.pkl`) for improved accuracy on categorical features |
| 2 | **Pipeline artifacts** | Extracted preprocessing into `pipeline_artifacts.pkl` — consistent feature encoding across training and inference |
| 3 | **Async job queue** | Added **Celery + Redis** worker (`ml-worker` container); all ML endpoints now support `?async_mode=true` |
| 4 | **Job status endpoint** | `GET /api/v1/jobs/{task_id}` polls Celery task state (PENDING → SUCCESS / FAILURE) |
| 5 | **Modular backend** | Split monolithic `main.py` into `routers/`, `ml/`, `core/`, `schemas/`, and `tasks/` packages |
| 6 | **Predict UI** | New `/predict` page in the Next.js frontend with a form and result card |
| 7 | **Metadata endpoint** | `GET /api/v1/metadata` exposes available categories for dynamic form population |
| 8 | **ML feature pipeline** | Added `ml/features.py` and `ml/encoders.py` for clean, testable feature engineering |

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 ML Prediction | CatBoost model trained on 300k+ campaigns for success/failure classification |
| 🔎 Semantic Search | SentenceTransformers + pgvector finds campaigns similar to yours |
| ⚡ Async Queue | Celery workers process long-running ML jobs without blocking the API |
| 📊 REST API | FastAPI backend with auto-generated Swagger documentation |
| 🖥️ Modern UI | Responsive Next.js frontend with Tailwind CSS |
| 🐳 Containerized | Full Docker Compose setup — one command to run everything |
| 💾 Persistent DB | PostgreSQL with pgvector extension for AI embeddings |

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          User Browser                               │
│                       http://localhost:3000                         │
└────────────────────────────┬────────────────────────────────────────┘
                             │  HTTP / REST
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Next.js Frontend (Port 3000)                     │
│                                                                     │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │  /predict    │  │  /              │  │  lib/api.ts          │  │
│  │  PredictForm │  │  Home Page      │  │  (API client layer)  │  │
│  │  PredictResult│ │                 │  │                      │  │
│  └──────────────┘  └──────────────────┘  └──────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │  HTTP / REST (Port 8000)
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  FastAPI ML Backend (Port 8000)                     │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                         Routers                              │   │
│  │  /health  /metadata  /predict  /recommend  /projects  /jobs  │   │
│  └──────────────────────────┬─────────────────────────────────┘    │
│                              │                                       │
│  ┌───────────────────────────▼──────────────────────────────────┐   │
│  │                       ML Layer                               │   │
│  │                                                              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │   │
│  │  │ ml/service.py│  │ml/features.py│  │  ml/encoders.py  │   │   │
│  │  │ (model load) │  │(feature eng.)│  │ (label encoding) │   │   │
│  │  └──────┬───────┘  └──────────────┘  └──────────────────┘   │   │
│  │         │                                                     │   │
│  │  ┌──────▼───────────────────────────────────────────────┐   │   │
│  │  │              Loaded Model Artifacts                  │   │   │
│  │  │  kca_classifier_v2.pkl   pipeline_artifacts.pkl      │   │   │
│  │  │  (CatBoost Classifier)   (Preprocessing Pipeline)    │   │   │
│  │  └──────────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                      Tasks Layer                             │   │
│  │  tasks/  →  dispatches jobs to Celery via celery_app.py      │   │
│  └──────────────────────────────────────────────────────────────┘   │
└────────┬──────────────────────────────────────────┬─────────────────┘
         │  SQL + pgvector queries                  │  Celery tasks
         ▼                                          ▼
┌─────────────────────┐                ┌──────────────────────────────┐
│  PostgreSQL + pgvec │                │         Redis (Port 6379)    │
│  (Port 5432)        │                │                              │
│                     │                │  DB 0 → Celery broker        │
│  • campaigns table  │                │  DB 1 → Celery result store  │
│  • embeddings (vec) │                └──────────────┬───────────────┘
│  • pgvector ANN     │                               │  job dispatch
└─────────────────────┘                               ▼
                                       ┌──────────────────────────────┐
                                       │    Celery ML Worker          │
                                       │    (kca-ml-worker container) │
                                       │                              │
                                       │  • predict task              │
                                       │  • recommend task            │
                                       │  • same ML model loaded      │
                                       └──────────────────────────────┘
```

### Container Architecture (Docker Compose)

```
docker-compose.yml
│
├── kca-ml-api        (ml-backend)   — FastAPI + Uvicorn   :8000
├── kca-ml-worker     (ml-worker)    — Celery worker (solo pool)
├── frontend          (frontend)     — Next.js dev server  :3000
├── kca-postgres      (db)           — PostgreSQL + pgvector :5432
└── kca-redis         (redis)        — Redis 7 Alpine       :6379
```

All containers share a single bridge network with MTU 1450. The `ml-backend` and `ml-worker` mount `./backend` as a volume so code changes reload without rebuilding.

### Backend Module Structure

```
backend/
├── main.py                  # App factory — mounts all routers & CORS
├── celery_app.py            # Celery instance & broker config
│
├── core/
│   ├── config.py            # Pydantic Settings (env vars, model paths)
│   └── lifespan.py          # FastAPI lifespan — model preload on startup
│
├── ml/
│   ├── state.py             # Global singleton holding loaded model objects
│   ├── service.py           # ensure_models_loaded() — lazy loader
│   ├── features.py          # Feature engineering & transformation
│   └── encoders.py          # Label/ordinal encoders used at inference
│
├── routers/
│   ├── health.py            # GET  /api/v1/health
│   ├── metadata.py          # GET  /api/v1/metadata  (categories)
│   ├── predict.py           # POST /api/v1/predict   (sync + async)
│   ├── recommend.py         # POST /api/v1/recommend (sync + async)
│   ├── projects.py          # GET  /api/v1/projects  (DB browse)
│   └── jobs.py              # GET  /api/v1/jobs/{id} (Celery poll)
│
├── schemas/
│   └── campaign.py          # Pydantic request/response models
│
├── tasks/                   # Celery task definitions
├── db/                      # SQLAlchemy session & ORM models
│
└── models/
    ├── kca_classifier_v2.pkl       # CatBoost classifier
    └── pipeline_artifacts.pkl      # Preprocessing pipeline
```

### ML Inference Flow

```
HTTP POST /api/v1/predict
         │
         ▼
  schemas/campaign.py          ← validate & parse request body
         │
         ▼
  ml/features.py               ← engineer raw features from input
         │
         ▼
  ml/encoders.py               ← apply label/ordinal encoding
         │
         ▼
  pipeline_artifacts.pkl       ← scikit-learn pipeline (scaling, etc.)
         │
         ▼
  kca_classifier_v2.pkl        ← CatBoost predict_proba()
         │
         ▼
  JSON response                ← { success_probability, prediction, ... }
```

For async calls (`?async_mode=true`), the same pipeline runs inside a **Celery task**. The API immediately returns a `task_id`; the client polls `GET /api/v1/jobs/{task_id}` until the result is ready.

---

## 🛠️ Tech Stack

### Frontend
- **[Next.js 14](https://nextjs.org)** — React framework with App Router
- **[Tailwind CSS](https://tailwindcss.com)** — Utility-first CSS framework
- **[Lucide Icons](https://lucide.dev)** — Clean, consistent icon library

### Backend
- **[FastAPI](https://fastapi.tiangolo.com)** — High-performance Python API framework
- **[Pandas](https://pandas.pydata.org)** / **[Scikit-learn](https://scikit-learn.org)** — Data processing and preprocessing
- **[Celery](https://docs.celeryq.dev)** — Distributed task queue for async ML jobs

### Machine Learning
- **[CatBoost](https://catboost.ai)** — Gradient boosting model optimised for categorical features
- **[SentenceTransformers](https://www.sbert.net)** — Semantic text embeddings for similarity search

### Database & Infrastructure
- **[PostgreSQL](https://postgresql.org)** + **[pgvector](https://github.com/pgvector/pgvector)** — Relational DB with native vector search
- **[Redis](https://redis.io)** — Celery message broker and result backend
- **[Docker](https://docker.com)** & **Docker Compose** — Containerized microservices deployment

---

## 📁 Project Structure

```
kca-microservices/
├── backend/                    # FastAPI application & ML models
│   ├── core/                   # Config and lifespan management
│   ├── ml/                     # Model loading, feature engineering, encoders
│   ├── routers/                # API route handlers
│   ├── schemas/                # Pydantic request/response models
│   ├── tasks/                  # Celery task definitions
│   ├── db/                     # SQLAlchemy session and ORM models
│   ├── models/                 # Trained model files (.pkl)
│   ├── celery_app.py           # Celery app instance
│   ├── main.py                 # FastAPI app factory
│   └── requirements.txt        # Python dependencies
│
├── frontend/                   # Next.js web application
│   ├── app/                    # Next.js App Router pages
│   ├── components/             # React components (PredictForm, PredictResult, …)
│   ├── lib/                    # API client (api.ts)
│   ├── types/                  # TypeScript type definitions
│   └── hooks/                  # Custom React hooks
│
├── db-init/                    # PostgreSQL initialization scripts
│   └── init.sql                # Schema creation & pgvector setup
│
├── docker-compose.yml          # Multi-container orchestration
├── migrate_to_db.py            # One-time data ingestion script
└── README.md
```

---

## ⚡ Getting Started

### Prerequisites

- **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** (includes Docker Compose)
- **[Python 3.10+](https://python.org/downloads/)** (for the data migration script)
- Trained model files (`.pkl`) placed inside `backend/models/`

---

### Step 1 — Start All Services

```bash
docker-compose up -d
```

This spins up **5 containers**:

| Container | Service | Port |
|---|---|---|
| `kca-postgres` | PostgreSQL + pgvector | `5432` |
| `kca-redis` | Redis (Celery broker) | `6379` |
| `kca-ml-api` | FastAPI + ML Models | `8000` |
| `kca-ml-worker` | Celery worker | — |
| `frontend` | Next.js Web UI | `3000` |

```bash
# Check container status
docker-compose ps
```

---

### Step 2 — Import Data *(First-time only)*

```bash
pip install psycopg2-binary pandas numpy
python migrate_to_db.py
```

> Data persists across restarts via Docker volumes — run this only once.

---

### Step 3 — Access the Application

| Interface | URL |
|---|---|
| 🌐 **Web Application** | http://localhost:3000 |
| ⚙️ **API Docs (Swagger)** | http://localhost:8000/docs |
| 📡 **API Root** | http://localhost:8000 |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Service health check |
| `GET` | `/api/v1/metadata` | Available categories for form population |
| `POST` | `/api/v1/predict` | Predict campaign success (sync) |
| `POST` | `/api/v1/predict?async_mode=true` | Queue prediction as Celery job |
| `POST` | `/api/v1/recommend` | Recommend similar projects (sync) |
| `POST` | `/api/v1/recommend?async_mode=true&top_k=6` | Queue recommendation as Celery job |
| `GET` | `/api/v1/jobs/{task_id}` | Poll Celery job status / result |

### Async Job Example

```bash
# Submit async job
curl -X POST "http://localhost:8000/api/v1/predict?async_mode=true" \
  -H "Content-Type: application/json" \
  -d '{"category": "Technology", "goal_usd": 50000, "duration_days": 30}'
# → { "task_id": "d4a8f8df-...", "status": "PENDING" }

# Poll result
curl "http://localhost:8000/api/v1/jobs/d4a8f8df-..."
```

---

## 🤖 Machine Learning Details

### Model: CatBoost Classifier v2
- **Training data:** 300,000+ historical Kickstarter campaigns
- **Target variable:** Campaign outcome (`successful` / `failed`)
- **Why CatBoost:** Native categorical feature handling without manual encoding overhead

### Vector Similarity Search
- Campaign descriptions encoded via **SentenceTransformers** (`all-MiniLM-L6-v2`)
- Stored in **PostgreSQL + pgvector** for fast approximate nearest-neighbor (ANN) search
- Returns the most semantically similar historical campaigns as references

---

## 🛑 Stopping the Application

```bash
docker-compose down          # stop containers, keep data
docker-compose down -v       # stop containers + delete volumes
```

---

## 🧪 Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Celery worker (separate terminal):**
```bash
cd backend
celery -A celery_app.celery_app worker --loglevel=info --pool=solo
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## 🗺️ Roadmap

- [ ] Add campaign category breakdown charts
- [ ] Support multi-language campaign descriptions
- [ ] Export prediction report as PDF
- [ ] User authentication & saved campaign history
- [ ] Model retraining pipeline with new campaign data

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

Built with ❤️ as part of a Machine Learning & Full-Stack Development project.

If you found this project useful, please consider giving it a ⭐ on GitHub!
