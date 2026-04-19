# 🚀 Kickstarter Campaign Advisor (KCA)

> **An AI-powered web application that predicts Kickstarter campaign success using Machine Learning and Vector Similarity Search.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-000000?style=flat&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)](https://docker.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?style=flat&logo=postgresql&logoColor=white)](https://postgresql.org)

---

## 📖 Overview

**Kickstarter Campaign Advisor (KCA)** helps creators evaluate the potential success of their crowdfunding campaigns before launching. By analyzing over **300,000 historical Kickstarter campaigns**, the system uses an **XGBoost** classification model and **AI-powered Vector Search** to provide:

- 🎯 **Success probability score** for your campaign
- 🔍 **Similar past campaigns** as real-world references
- 💡 **Actionable insights** to improve campaign structure

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 ML Prediction | XGBoost model trained on 300k+ campaigns for success/failure classification |
| 🔎 Semantic Search | SentenceTransformers + pgvector finds campaigns similar to yours |
| ⚡ REST API | FastAPI backend with auto-generated Swagger documentation |
| 🖥️ Modern UI | Responsive Next.js frontend with Tailwind CSS |
| 🐳 Containerized | Full Docker Compose setup — one command to run everything |
| 💾 Persistent DB | PostgreSQL with pgvector extension for AI embeddings |

---

## 🛠️ Tech Stack

### Frontend
- **[Next.js 14](https://nextjs.org)** — React framework with App Router
- **[Tailwind CSS](https://tailwindcss.com)** — Utility-first CSS framework
- **[Lucide Icons](https://lucide.dev)** — Clean, consistent icon library

### Backend
- **[FastAPI](https://fastapi.tiangolo.com)** — High-performance Python API framework
- **[Pandas](https://pandas.pydata.org)** / **[Scikit-learn](https://scikit-learn.org)** — Data processing and preprocessing

### Machine Learning
- **[XGBoost](https://xgboost.readthedocs.io)** — Gradient boosting model for campaign success prediction
- **[SentenceTransformers](https://www.sbert.net)** — Semantic text embeddings for similarity search

### Database & Infrastructure
- **[PostgreSQL](https://postgresql.org)** + **[pgvector](https://github.com/pgvector/pgvector)** — Relational DB with native vector search
- **[Docker](https://docker.com)** & **Docker Compose** — Containerized microservices deployment

---

## 📁 Project Structure

```
kca-microservices/
├── backend/                    # FastAPI application & ML models
│   ├── models/                 # Trained model files (.pkl, .npy, .csv)
│   ├── main.py                 # API route definitions & business logic
│   └── requirements.txt        # Python dependencies
│
├── frontend/                   # Next.js web application
│   ├── src/
│   │   └── app/                # Pages and React components
│   ├── package.json            # Node.js dependencies
│   └── tailwind.config.ts      # Tailwind configuration
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

Make sure you have the following installed on your machine:

- **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** (includes Docker Compose)
- **[Python 3.10+](https://python.org/downloads/)** (for the data migration script)
- Trained model files (`.pkl`) placed inside `backend/models/`

---

### Step 1 — Start All Services

From the project root directory, run:

```bash
docker-compose up -d
```

This will spin up **5 containers**:

| Container | Service | Port |
|---|---|---|
| `db` | PostgreSQL + pgvector | `5432` |
| `redis` | Celery broker/result backend | `6379` |
| `ml-backend` | FastAPI + ML Models | `8000` |
| `ml-worker` | Celery worker for ML jobs | - |
| `frontend` | Next.js Web UI | `3000` |

Wait until all containers show a **Running** status before proceeding.

```bash
# Check container status
docker-compose ps
```

---

### Step 2 — Import Data into Database *(First-time only)*

Install the required Python libraries:

```bash
pip install psycopg2-binary pandas numpy
```

Then run the migration script to load the knowledge base into PostgreSQL:

```bash
python migrate_to_db.py
```

> ✅ The script will display a success message once all records have been imported. This step only needs to be done **once** — data persists across restarts thanks to Docker volumes.

---

### Step 3 — Access the Application

Once all services are running and data is imported:

| Interface | URL |
|---|---|
| 🌐 **Web Application** | http://localhost:3000 |
| ⚙️ **API Documentation (Swagger UI)** | http://localhost:8000/docs |
| 📡 **API Root** | http://localhost:8000 |

---

## 🔌 API Endpoints

All endpoints are documented interactively at `http://localhost:8000/docs`.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/predict` | Predict campaign success probability (sync by default) |
| `POST` | `/api/v1/recommend` | Recommend similar projects (sync by default) |
| `POST` | `/api/v1/predict?async_mode=true` | Queue prediction as Celery job |
| `POST` | `/api/v1/recommend?async_mode=true&top_k=6` | Queue recommendation as Celery job |
| `GET` | `/api/v1/jobs/{task_id}` | Check job status/result |
| `GET` | `/api/v1/health` | Service health check |

### Job Queue Example (Celery)

Submit async prediction job:

```bash
curl -X POST "http://localhost:8000/api/v1/predict?async_mode=true" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "Technology",
    "goal_usd": 50000,
    "duration_days": 30,
    "launch_month": 4
  }'
```

Sample response:

```json
{
  "success": true,
  "task_id": "d4a8f8df-3f77-4d20-86a1-57d2b2f0f4af",
  "status": "PENDING",
  "status_endpoint": "/api/v1/jobs/d4a8f8df-3f77-4d20-86a1-57d2b2f0f4af"
}
```

Poll job status:

```bash
curl "http://localhost:8000/api/v1/jobs/d4a8f8df-3f77-4d20-86a1-57d2b2f0f4af"
```

### Example Request — `/predict`

```json
POST /predict
{
  "name": "Eco-friendly Water Bottle",
  "category": "product design",
  "goal": 15000,
  "duration_days": 30,
  "description": "A sustainable, reusable water bottle made from recycled ocean plastics."
}
```

### Example Response

```json
{
  "success_probability": 0.73,
  "prediction": "successful",
  "confidence": "high",
  "similar_campaigns": [...]
}
```

---

## 🤖 Machine Learning Details

### Model: XGBoost Classifier
- **Training data:** 300,000+ historical Kickstarter campaigns
- **Target variable:** Campaign outcome (`successful` / `failed`)
- **Key features:** funding goal, campaign duration, category, description sentiment, and more

### Vector Similarity Search
- Campaign descriptions are encoded using **SentenceTransformers** into high-dimensional embeddings
- Stored in **PostgreSQL + pgvector** for fast approximate nearest-neighbor (ANN) search
- Returns the most semantically similar historical campaigns as contextual references

---

## 🛑 Stopping the Application

To stop all running containers:

```bash
docker-compose down
```

> **Note:** Your database data is safe. Docker volumes persist all data between restarts. To remove data volumes as well, run `docker-compose down -v`.

---

## 🧪 Development

To run services individually for development:

**Backend (FastAPI):**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend (Next.js):**
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

Contributions are welcome! Please follow these steps:

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