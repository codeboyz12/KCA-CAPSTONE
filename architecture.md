# KCA System Architecture

```mermaid
graph TB
    subgraph Client["Client Layer"]
        USER["👤 User Browser"]
    end

    subgraph Frontend["Frontend — Next.js 16 / React 19 / Tailwind CSS  (Port 3000)"]
        direction TB
        LANDING["Landing Page\nProject list · Semantic search · Detail modal"]
        PREDICT_UI["Predict Page\nCampaign form · Result card · Similar projects"]
    end

    subgraph API["ML Backend API — FastAPI / Python 3.10  (Port 8000)"]
        direction TB
        subgraph Browse["Data Browsing"]
            PROJECTS["/api/v1/projects\nPaginated list"]
            SEARCH["/api/v1/search\nSemantic vector search\n+ lru_cache(256)"]
            STATS["/api/v1/stats/categories\n/api/v1/stats/predictions"]
            META["/api/v1/metadata\n/api/v1/metadata/main-categories"]
        end
        subgraph Inference["ML Inference"]
            PREDICT["/api/v1/predict\nSync & Async"]
            RECOMMEND["/api/v1/recommend\nStructural + semantic match"]
        end
        subgraph Ops["Operations"]
            RETRAIN["/api/v1/admin/retrain\nTrigger job"]
            JOBS["/api/v1/jobs/{task_id}\nPoll status"]
        end
        EMBEDDER["SentenceTransformer\nall-MiniLM-L6-v2\n(shared, loaded once)"]
        CATBOOST["CatBoost Classifier\n+ SHAP Explainer\n+ Feature Pipeline"]
    end

    subgraph Queue["Task Queue — Celery 5.4"]
        WORKER["Celery Worker\nML Inference (async)\nModel Retraining"]
    end

    subgraph Storage["Data Layer"]
        PG[("PostgreSQL 15 + pgvector  (Port 5432)\n─────────────────────────────\nprojects  229k+ rows\n  text_embedding vector(384)  ← unified sentence\ncategories  FK normalisation\nprediction_log  drift audit\ncategory_stats  materialized view\n─────────────────────────────\nHNSW: text_embedding  (m=16, ef=64)\nB-tree: category · state · created_at")]
        REDIS[("Redis 7  (Port 6379)\n─────────────────────────────\nDB 0 — Celery broker\nDB 1 — Task result backend")]
        MLFLOW[("MLflow 2.13  (Port 5001)\n─────────────────────────────\nSQLite — run metadata\n/mlflow/artifacts — model binaries")]
    end

    %% Client to Frontend
    USER -- "HTTP" --> LANDING
    USER -- "HTTP" --> PREDICT_UI

    %% Frontend to API
    LANDING -- "GET /projects\nGET /search" --> Browse
    PREDICT_UI -- "POST /predict\nPOST /recommend" --> Inference
    PREDICT_UI -- "POST /retrain\nGET /jobs" --> Ops

    %% Embedder used by both search and recommend
    SEARCH -- "encode query" --> EMBEDDER
    RECOMMEND -- "encode campaign input" --> EMBEDDER
    EMBEDDER -- "HNSW <=> query" --> PG

    %% Inference pipeline
    PREDICT --> CATBOOST
    CATBOOST -- "read features\nwrite prediction_log" --> PG

    %% Stats & metadata
    STATS -- "SELECT category_stats" --> PG
    META -- "SELECT categories" --> PG
    PROJECTS -- "SELECT projects" --> PG

    %% Async path
    RETRAIN -- "enqueue" --> REDIS
    JOBS -- "fetch result" --> REDIS
    REDIS -- "dequeue" --> WORKER
    WORKER -- "load training data" --> PG
    WORKER -- "log metrics / save model" --> MLFLOW
    WORKER -- "store result" --> REDIS

    %% Styling
    classDef client   fill:#4A90D9,stroke:#2C5F8A,color:#fff
    classDef frontend fill:#6C5CE7,stroke:#4A3AA8,color:#fff
    classDef api      fill:#00B894,stroke:#007A63,color:#fff
    classDef queue    fill:#FDCB6E,stroke:#C9A140,color:#333
    classDef db       fill:#E17055,stroke:#A84F37,color:#fff

    class USER client
    class LANDING,PREDICT_UI frontend
    class PROJECTS,SEARCH,STATS,META,PREDICT,RECOMMEND,RETRAIN,JOBS,EMBEDDER,CATBOOST api
    class WORKER queue
    class PG,REDIS,MLFLOW db
```

---

## Request Flows

### 1 — Semantic Search (Landing page search box)
```
Browser → Next.js (400ms debounce or button click)
  → GET /api/v1/search?q=...&page=1&limit=12

FastAPI:
  lru_cache(256): if query seen before → skip model, return cached vector
  else: SentenceTransformer.encode(query)  ~20ms
  → pgvector HNSW cosine search (text_embedding <=>)  ~5ms
  → paginate top-120 results in Python
  → return ProjectsResponse (same shape as /projects)
```

### 2 — Synchronous Prediction
```
Browser → Next.js → POST /api/v1/predict

FastAPI:
  → Feature engineering (build_features)
  → CatBoost inference  →  prob_success, is_viable
  → CatBoost native SHAP  →  top-5 feature impacts
  → category_stats lookup  →  success_rate, median_goal, competition
  → write prediction_log → PostgreSQL
  → return enriched result
```

### 3 — Similar Campaign Recommendations
```
Browser → Next.js → POST /api/v1/recommend

FastAPI:
  → Build canonical sentence:
      "{name}. A {main_category} Kickstarter project in the {category}
       subcategory, with a ${goal_usd} funding goal and a {duration_days}-day
       campaign."
  → SentenceTransformer.encode(sentence)  →  384-dim query vector
  → pgvector HNSW fetch top-100 by cosine distance
  → re-score each result:
      score = 0.6 × cosine_sim + 0.2 × category_match + 0.2 × category_prior
  → return top-k sorted by score
```

### 4 — Asynchronous Retraining (MLOps)
```
Browser → POST /api/v1/admin/retrain
  → FastAPI enqueues Celery task → Redis DB 0
  → return { task_id }

Browser polls GET /api/v1/jobs/{task_id}
  → Redis DB 1 returns { status, result }

Celery Worker:
  → Load all projects from PostgreSQL
  → Feature engineering (50+ features)
  → Train CatBoost model
  → Quality gate: AUC ≥ 0.65  AND  F1 ≥ 0.55
      PASS → save model artifact + log run → MLflow
      FAIL → keep current model, log failed run
  → Write result → Redis DB 1
```

---

## Embedding Design

All vector search (both `/search` and `/recommend`) uses **one column: `text_embedding vector(384)`**.

Projects are embedded at ingest time using the canonical sentence template:

```
"{name}. A {main_category} Kickstarter project in the {category} subcategory,
 with a ${goal_usd:,.0f} funding goal and a {duration_days}-day campaign."
```

At query time:
- **`/search`**: raw query string is embedded and matched against `text_embedding`
- **`/recommend`**: user's campaign form data is converted with the same template and matched

Both use the same HNSW index — no separate struct/text split.
To regenerate embeddings: run `recompute_text_embs.py` inside the API container.

---

## Frontend Components

| Page | Component | Responsibility |
|---|---|---|
| `/` | `HeroSection` | Search box (400ms debounce + button) |
| `/` | `ProjectGrid` + `ProjectRow` | Paginated project table |
| `/` | `ProjectDetailModal` | Category benchmarks + "Use as Template" CTA |
| `/` | `ActionMenu` | Link to predictor |
| `/predict` | `PredictForm` | Campaign input form (pre-fills from URL params) |
| `/predict` | `PredictResult` | Score · SHAP bars · category stats · competition badge |
| `/predict` | `SimilarProjects` | Recommendation cards from `/recommend` |

---

## Services & Ports

| Service | Image / Stack | Port | Purpose |
|---|---|---|---|
| `frontend` | Node 20 / Next.js 16 | 3000 | Web UI |
| `kca-ml-api` | Python 3.10 / FastAPI | 8000 | REST API + ML inference |
| `kca-ml-worker` | Python 3.10 / Celery | — | Async task execution |
| `kca-postgres` | PostgreSQL 15 + pgvector | 5432 | Primary data store + vector DB |
| `kca-redis` | Redis 7 alpine | 6379 | Broker (DB 0) + results (DB 1) |
| `kca-mlflow` | MLflow 2.13 | 5001 | Experiment tracking + model registry |

---

## Key Data Stores

| Store | Type | Key Detail |
|---|---|---|
| `projects` | Table | 229k+ campaigns; `text_embedding vector(384)` — unified sentence embedding |
| `categories` | Table | FK normalisation; `main_category` field |
| `prediction_log` | Table | Every `/predict` call logged — feeds drift monitoring |
| `category_stats` | Materialized View | Pre-aggregated success rates, median goals, avg durations |
| HNSW index on `text_embedding` | Index (pgvector) | `m=16, ef_construction=64` — sub-10ms cosine search on 229k rows |
| Redis DB 0 | Queue | Celery task broker |
| Redis DB 1 | KV Store | Celery result backend (TTL-based) |
| MLflow artifacts | File store | CatBoost model binaries (`/mlflow/artifacts`) |

---

## ML Models Loaded at Startup

| Model | File | Used by |
|---|---|---|
| CatBoost classifier | `kca_classifier_v2.pkl` | `/predict` |
| Feature pipeline artifacts | `pipeline_artifacts.pkl` | `/predict` |
| SentenceTransformer `all-MiniLM-L6-v2` | Downloaded from HuggingFace | `/search`, `/recommend` |
