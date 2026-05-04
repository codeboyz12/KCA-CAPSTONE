import joblib
import pandas as pd
from sentence_transformers import SentenceTransformer

from core.config import settings
from db.session import get_db_connection
from schemas.campaign import CampaignInput
from ml.state import ml
from ml.features import build_features

W_TEXT, W_CAT, W_STRUCT, W_PRIOR = 0.3, 0.2, 0.3, 0.2


def ensure_models_loaded() -> None:
    if ml.resources_loaded:
        return

    ml.clf_model          = joblib.load(settings.MODEL_CLASSIFIER)
    ml.pipeline_artifacts = joblib.load(settings.MODEL_PIPELINE_ARTIFACTS)
    ml.scaler             = joblib.load(settings.MODEL_SCALER)
    ml.embedder           = SentenceTransformer(settings.SENTENCE_MODEL)

    conn = get_db_connection()
    cur = conn.cursor()
    # use materialized view instead of full GROUP BY scan
    cur.execute("SELECT category, success_rate FROM category_stats;")
    ml.category_prior = {row[0]: float(row[1]) for row in cur.fetchall()}
    cur.close()
    conn.close()
    ml.resources_loaded = True


def _log_prediction(data: CampaignInput, prob: float, source: str = "api") -> None:
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO prediction_log
                (category, goal_usd, duration_days, prob_success, is_viable, source)
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (data.category, data.goal_usd, data.duration_days,
             round(prob, 4), prob > 0.5, source),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass  # never let logging break the prediction response


def predict_campaign_payload(payload: dict, source: str = "api") -> dict:
    ensure_models_loaded()
    data = CampaignInput(**payload)

    feature_df = build_features(data.model_dump(), ml.pipeline_artifacts)
    prob_success = float(ml.clf_model.predict_proba(feature_df)[0][1])

    _log_prediction(data, prob_success, source)

    return {
        "success": True,
        "prediction": {
            "probability_percentage": round(prob_success * 100, 2),
            "is_viable": prob_success > 0.5,
        },
    }


def _build_vectors(data: CampaignInput) -> tuple[str, str]:
    user_text = (
        f"A {data.category} project needing ${data.goal_usd} in {data.duration_days} days."
    )
    text_emb   = ml.embedder.encode([user_text])[0].tolist()
    struct_emb = ml.scaler.transform([[data.goal_usd, data.duration_days]])[0].tolist()

    def to_pg(v: list[float]) -> str:
        return "[" + ",".join(map(str, v)) + "]"

    return to_pg(text_emb), to_pg(struct_emb)


def _score(row: tuple, category: str) -> dict:
    p_id, p_name, p_cat, p_goal, p_dur, p_state, text_sim, struct_sim = row
    cat_match = 1.0 if p_cat == category else 0.0
    prior_val = ml.category_prior.get(p_cat, 0.0)
    total = (
        (W_TEXT * text_sim)
        + (W_CAT * cat_match)
        + (W_STRUCT * struct_sim)
        + (W_PRIOR * prior_val)
    )
    return {
        "project_id":      p_id,
        "name":            p_name,
        "category":        p_cat,
        "goal_usd":        p_goal,
        "duration_days":   p_dur,
        "state":           "Successful" if p_state == 1 else "Failed",
        "similarity_score": round(total, 4),
    }


def recommend_campaign_payload(payload: dict, top_k: int = 3) -> dict:
    ensure_models_loaded()
    data = CampaignInput(**payload)
    text_vec, struct_vec = _build_vectors(data)

    query = """
        SELECT project_id, name, category, goal_usd, duration_days, state_binary,
               (1 - (text_embedding   <=> %s::vector)) AS text_sim,
               (1 - (struct_embedding <=> %s::vector)) AS struct_sim
        FROM projects
        ORDER BY text_embedding <=> %s::vector
        LIMIT 100;
    """

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, (text_vec, struct_vec, text_vec))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    scored   = [_score(row, data.category) for row in rows]
    top_list = sorted(scored, key=lambda x: x["similarity_score"], reverse=True)[:top_k]

    return {
        "success":          True,
        "target_category":  data.category,
        "recommended_cases": top_list,
    }
