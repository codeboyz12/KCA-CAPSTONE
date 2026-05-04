# 🚀 Kickstarter Campaign Advisor (KCA)

> **An AI-powered web application that predicts Kickstarter campaign success using Machine Learning, Vector Similarity Search, and an automated MLOps retraining pipeline.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-000000?style=flat&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)](https://docker.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?style=flat&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat&logo=redis&logoColor=white)](https://redis.io)
[![Celery](https://img.shields.io/badge/Celery-5.4-37814A?style=flat)](https://docs.celeryq.dev)
[![CatBoost](https://img.shields.io/badge/CatBoost-1.2-yellow?style=flat)](https://catboost.ai)
[![MLflow](https://img.shields.io/badge/MLflow-2.13-0194E2?style=flat&logo=mlflow&logoColor=white)](https://mlflow.org)

---

## 📖 Overview

**Kickstarter Campaign Advisor (KCA)** helps creators evaluate the potential success of their crowdfunding campaigns before launching. By analyzing over **300,000 historical Kickstarter campaigns**, the system provides:

- 🎯 **Success probability score** for your campaign
- 🔍 **Similar past campaigns** as real-world references
- ⚡ **Asynchronous job queue** for non-blocking ML inference
- 🔄 **Automated retraining pipeline** — new data triggers a full retrain with quality gate and MLflow tracking

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 ML Prediction | CatBoost model trained on 300k+ campaigns for success/failure classification |
| 🔎 Semantic Search | SentenceTransformers + pgvector finds campaigns similar to yours |
| ⚡ Async Queue | Celery workers process long-running ML jobs without blocking the API |
| 🔄 Auto Retrain | Add new data → trigger retrain → quality gate → MLflow registry |
| 📊 Experiment Tracking | MLflow logs every training run with params, metrics, and artifacts |
| 🖥️ Modern UI | Responsive Next.js frontend with Tailwind CSS |
| 🐳 Containerized | Full Docker Compose setup — one command to run everything |

---

## 🛠️ Tech Stack

### Frontend
- **[Next.js 14](https://nextjs.org)** — React framework with App Router
- **[Tailwind CSS](https://tailwindcss.com)** — Utility-first CSS framework

### Backend
- **[FastAPI](https://fastapi.tiangolo.com)** — High-performance Python API framework
- **[Celery](https://docs.celeryq.dev)** + **[Redis](https://redis.io)** — Async task queue

### Machine Learning & MLOps
- **[CatBoost](https://catboost.ai)** — Gradient boosting classifier
- **[SentenceTransformers](https://www.sbert.net)** — Semantic text embeddings
- **[MLflow](https://mlflow.org)** — Experiment tracking and model registry

### Database & Infrastructure
- **[PostgreSQL](https://postgresql.org)** + **[pgvector](https://github.com/pgvector/pgvector)** — Relational DB with vector search
- **[Docker](https://docker.com)** & **Docker Compose** — Containerized microservices

---

## 📁 Project Structure

```
kca-microservices/
├── backend/
│   ├── core/              # Config and lifespan management
│   ├── ml/                # Model loading, feature engineering, encoders
│   ├── routers/           # API route handlers (predict, recommend, admin, jobs)
│   ├── schemas/           # Pydantic request/response models
│   ├── tasks/             # Celery tasks (predict, recommend, retrain)
│   ├── db/                # Database session
│   ├── models/            # Trained model files (.pkl, .cbm)
│   ├── celery_app.py      # Celery instance
│   ├── main.py            # FastAPI app factory
│   └── requirements.txt
│
├── frontend/              # Next.js web application
│   ├── app/               # App Router pages
│   ├── components/        # React components
│   ├── lib/               # API client
│   └── types/             # TypeScript types
│
├── scripts/
│   └── add_samples.py     # Insert synthetic campaign rows for retraining demo
│
├── db-init/               # PostgreSQL init scripts
├── docker-compose.yml     # 6-service orchestration
├── migrate_to_db.py       # One-time data ingestion
├── MLOPS_DESIGN.md        # MLOps system design document
├── DEMO.md                # Step-by-step demo guide
└── README.md
```

---

## ⚡ Getting Started

### Prerequisites

- **[Docker Desktop](https://www.docker.com/products/docker-desktop/)**
- **[Python 3.10+](https://python.org/downloads/)** (for migration and scripts)
- Trained model files (`.pkl`) inside `backend/models/`

### Step 1 — Start All Services

```bash
docker compose up -d
```

**6 containers:**

| Container | Service | Port |
|---|---|---|
| `kca-postgres` | PostgreSQL + pgvector | `5432` |
| `kca-redis` | Redis | `6379` |
| `kca-ml-api` | FastAPI + ML Models | `8000` |
| `kca-ml-worker` | Celery worker | — |
| `frontend` | Next.js | `3000` |
| `kca-mlflow` | MLflow Tracking Server | `5001` |

```bash
docker compose ps
```

### Step 2 — Import Data *(First-time only)*

```bash
pip install psycopg2-binary pandas numpy
python migrate_to_db.py
```

### Step 3 — Access the Application

| Interface | URL |
|---|---|
| 🌐 Web Application | http://localhost:3000 |
| ⚙️ API Docs (Swagger) | http://localhost:8000/docs |
| 📊 MLflow UI | http://localhost:5001 |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/api/v1/metadata` | Available categories |
| `POST` | `/api/v1/predict` | Predict campaign success (sync) |
| `POST` | `/api/v1/predict?async_mode=true` | Queue prediction as Celery job |
| `POST` | `/api/v1/recommend` | Similar campaigns (sync) |
| `POST` | `/api/v1/recommend?async_mode=true` | Queue recommendation job |
| `GET` | `/api/v1/jobs/{task_id}` | Poll job status / result |
| `POST` | `/api/v1/admin/retrain` | Trigger model retraining |

---

## 🔄 MLOps — Retraining Pipeline

Add new data and retrain the model automatically:

```bash
# 1. Insert new campaign samples into the database
python scripts/add_samples.py --n 200

# 2. Trigger retraining via API
curl -X POST http://localhost:8000/api/v1/admin/retrain

# 3. Poll the job status
curl http://localhost:8000/api/v1/jobs/{task_id}

# 4. View training run in MLflow
open http://localhost:5001
```

**Retraining flow:**
```
New data in DB → Celery retrain task → CatBoost trains
                                             ↓
                                    Quality Gate
                                    AUC ≥ 0.65 & F1 ≥ 0.55
                                         ↓           ↓
                                       PASS         FAIL
                                         ↓           ↓
                                  Save model    Keep current
                                  + log to      model, alert
                                  MLflow
```

See [DEMO.md](DEMO.md) for the full step-by-step demo guide.

---

## 🛑 Stopping the Application

```bash
docker compose down        # stop, keep data
docker compose down -v     # stop + delete volumes
```

---

## 🧪 Development

**Backend:**
```bash
cd backend && pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Celery worker:**
```bash
cd backend
celery -A celery_app.celery_app worker --loglevel=info --pool=solo
```

**Frontend:**
```bash
cd frontend && npm install && npm run dev
```

---

## 🗺️ Roadmap

- [x] CatBoost model upgrade
- [x] Async job queue (Celery + Redis)
- [x] MLOps retraining pipeline with MLflow
- [ ] Scheduled auto-retrain (Celery beat)
- [ ] Campaign category breakdown charts
- [ ] Export prediction report as PDF
- [ ] User authentication & saved campaign history

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

Built with ❤️ as part of a Machine Learning & Full-Stack Development capstone project.
