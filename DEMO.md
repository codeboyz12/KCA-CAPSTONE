# KCA Demo Guide — MLOps Retrain Pipeline

## Prerequisites

All containers running:

```bash
docker compose ps
```

Expected output:

| Name | Status | Ports |
|---|---|---|
| kca-ml-api | running | 8000 |
| kca-ml-worker | running | — |
| frontend | running | 3000 |
| kca-postgres | running | 5432 |
| kca-redis | running | 6379 |
| kca-mlflow | running | 5001 |

---

## Step 1 — Show the Current System

Open **http://localhost:3000** — show the prediction page working.

Open **http://localhost:5001** — show MLflow UI (empty or existing runs).

> **Say:** "This is our ML backend. The model was trained manually before deployment. Now we'll show how MLOps automates the retraining cycle when new data arrives."

---

## Step 2 — Check Current Data in Database

```bash
docker exec kca-postgres psql -U kca_admin -d kca_database \
  -c "SELECT COUNT(*) AS total_rows FROM projects;"
```

Note the number — this is how many campaigns the model currently knows about.

---

## Step 3 — Insert New Campaign Samples

```bash
python scripts/add_samples.py --n 200
```

Expected output:
```
Inserted 200 new samples.
Total rows in projects table: XXXXX
```

Verify the count increased:

```bash
docker exec kca-postgres psql -U kca_admin -d kca_database \
  -c "SELECT COUNT(*) AS total_rows FROM projects;"
```

> **Say:** "We just simulated 200 new campaign results arriving — this is what would happen nightly in a real system."

---

## Step 4 — Trigger Retraining via API

```bash
curl -X POST http://localhost:8000/api/v1/admin/retrain
```

Expected response:
```json
{
  "success": true,
  "message": "Retraining job queued",
  "task_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "status": "PENDING",
  "status_endpoint": "/api/v1/jobs/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

Copy the `task_id`.

> **Say:** "One API call triggers the entire retraining pipeline. The job runs asynchronously in the Celery worker — the API stays responsive."

---

## Step 5 — Monitor Job Progress

Replace `{task_id}` with the value from Step 4:

```bash
curl http://localhost:8000/api/v1/jobs/{task_id}
```

Poll until `status` changes from `PENDING` → `STARTED` → `SUCCESS`:

```json
{
  "task_id": "xxxxxxxx-...",
  "status": "SUCCESS",
  "ready": true,
  "successful": true,
  "result": {
    "success": true,
    "n_samples": 300200,
    "auc_roc": 0.71,
    "f1_score": 0.67,
    "train_time_sec": 12.4,
    "gate_passed": true,
    "message": "Model retrained and saved to production."
  }
}
```

> **Say:** "The quality gate automatically checks AUC and F1 score. If the new model is not good enough, it gets rejected and the current model stays in production."

**Quality gate thresholds:**

| Metric | Threshold |
|---|---|
| AUC ROC | ≥ 0.65 |
| F1 Score | ≥ 0.60 |

---

## Step 6 — View Results in MLflow UI

Open **http://localhost:5001**

1. Click **kca-classifier** experiment
2. Click the latest run
3. Show:
   - **Parameters** tab — training config (iterations, learning rate, depth)
   - **Metrics** tab — AUC, F1, training time
   - **Tags** tab — `quality_gate: passed`, `triggered_by: retrain_endpoint`
   - **Artifacts** tab — registered model (`kca-retrained-classifier`)

> **Say:** "Every training run is fully logged — parameters, metrics, and the model artifact. We can compare any two runs side by side and know exactly which data and config produced which result."

**Compare runs (if you have 2+ runs):**
- Tick two runs → click **Compare** button
- Show the metric comparison chart

---

## Step 7 — Show the Model Registry

In MLflow UI → click **Models** tab in the top nav.

Show `kca-retrained-classifier` with version history.

> **Say:** "The model registry tracks every version. In a full pipeline, promoting a version from Staging to Production is the only step needed to deploy — no file copying, no container restart."

---

## Full Flow Summary (one slide)

```
New data added to DB
        ↓
POST /api/v1/admin/retrain
        ↓
Celery worker trains CatBoost on full dataset
        ↓
Quality gate: AUC ≥ 0.65 & F1 ≥ 0.60
        ↓
   PASS → model saved + logged to MLflow
   FAIL → rejected, current model stays
        ↓
GET /api/v1/jobs/{id} → full result with metrics
```

---

## Troubleshooting

**Job stuck at PENDING:**
```bash
# Check worker is running
docker compose logs ml-worker --tail 20
```

**MLflow not reachable from worker:**
```bash
# Check mlflow container is healthy
docker compose logs mlflow --tail 10
```

**Port 5001 not opening:**
```bash
# Restart mlflow container only
docker compose restart mlflow
```
