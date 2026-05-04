import os
import time
import joblib
import numpy as np
import pandas as pd
import mlflow
import mlflow.catboost
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, f1_score
from sklearn.preprocessing import LabelEncoder

from celery_app import celery_app
from core.config import settings
from db.session import get_db_connection
from ml.state import ml

AUC_THRESHOLD = 0.65
F1_THRESHOLD  = 0.55


def _load_data_from_db() -> pd.DataFrame:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT category, goal_usd, duration_days, state_binary FROM projects;"
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return pd.DataFrame(rows, columns=["category", "goal_usd", "duration_days", "state_binary"])


def _build_train_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    df = df.copy()

    df["goal_usd_log"]     = np.log1p(df["goal_usd"])
    df["goal_on_duration"] = df["goal_usd"] / (df["duration_days"] + 1)
    df["goal_per_week"]    = df["goal_usd"] / ((df["duration_days"] / 7) + 1)

    cat_stats = df.groupby("category")["state_binary"].agg(["mean", "count"]).rename(
        columns={"mean": "cat_success_rate", "count": "cat_project_count"}
    )
    df = df.merge(cat_stats, on="category", how="left")

    cat_goals = df.groupby("category")["goal_usd"].median().rename("cat_median_goal")
    df = df.merge(cat_goals, on="category", how="left")
    df["goal_vs_cat_median"] = df["goal_usd"] / (df["cat_median_goal"] + 1)

    le = LabelEncoder()
    df["category_enc"] = le.fit_transform(df["category"].astype(str))

    features = [
        "category_enc",
        "goal_usd_log",
        "goal_on_duration",
        "goal_per_week",
        "duration_days",
        "cat_success_rate",
        "cat_project_count",
        "goal_vs_cat_median",
    ]
    X = df[features].fillna(0).astype(float)
    y = df["state_binary"].astype(int)
    return X, y


@celery_app.task(name="tasks.retrain_model", bind=True)
def retrain_model_task(self):
    mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    mlflow.set_experiment("kca-classifier")

    self.update_state(state="STARTED", meta={"step": "loading data"})
    df = _load_data_from_db()
    n_samples = len(df)

    self.update_state(state="STARTED", meta={"step": "building features", "n_samples": n_samples})
    X, y = _build_train_features(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    params = {
        "iterations":    300,
        "learning_rate": 0.05,
        "depth":         6,
        "loss_function": "Logloss",
        "eval_metric":   "AUC",
        "random_seed":   42,
        "verbose":       False,
    }

    self.update_state(state="STARTED", meta={"step": "training"})
    start = time.time()
    model = CatBoostClassifier(**params)
    model.fit(X_train, y_train)
    train_time = round(time.time() - start, 2)

    self.update_state(state="STARTED", meta={"step": "evaluating"})
    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)
    auc    = round(float(roc_auc_score(y_test, y_prob)), 4)
    f1     = round(float(f1_score(y_test, y_pred)), 4)

    gate_passed = bool(auc >= AUC_THRESHOLD and f1 >= F1_THRESHOLD)

    with mlflow.start_run() as run:
        mlflow.log_params({**params, "n_samples": n_samples, "train_size": len(X_train)})
        mlflow.log_metrics({"auc_roc": auc, "f1_score": f1, "train_time_sec": train_time})
        mlflow.set_tags({
            "triggered_by": "retrain_endpoint",
            "quality_gate": "passed" if gate_passed else "failed",
        })

        if gate_passed:
            mlflow.catboost.log_model(model, artifact_path="model",
                                      registered_model_name="kca-retrained-classifier")

    if gate_passed:
        self.update_state(state="STARTED", meta={"step": "saving model"})
        model_path = settings.MODEL_RETRAINED
        model.save_model(model_path)

        ml.resources_loaded = False

    return {
        "success":      True,
        "n_samples":    n_samples,
        "auc_roc":      auc,
        "f1_score":     f1,
        "train_time_sec": train_time,
        "gate_passed":  gate_passed,
        "mlflow_run_id": run.info.run_id,
        "message": (
            "Model retrained and saved to production."
            if gate_passed
            else f"Quality gate failed — AUC={auc} (need {AUC_THRESHOLD}), F1={f1} (need {F1_THRESHOLD}). Model NOT deployed."
        ),
    }
