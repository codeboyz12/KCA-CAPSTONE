import joblib
import pandas as pd
from sentence_transformers import SentenceTransformer

from core.config import settings
from db.session import get_db_connection
from schemas.campaign import CampaignInput
from ml.state import ml
from ml.features import build_features

W_SIM, W_CAT, W_PRIOR = 0.6, 0.2, 0.2


def ensure_models_loaded() -> None:
    if ml.resources_loaded:
        return

    ml.clf_model          = joblib.load(settings.MODEL_CLASSIFIER)
    ml.pipeline_artifacts = joblib.load(settings.MODEL_PIPELINE_ARTIFACTS)
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


def _get_top_shap_factors(model, feature_df: pd.DataFrame, n: int = 5) -> list[dict]:
    try:
        from catboost import Pool
        cb = model.steps[-1][1]
        X_scaled = model[:-1].transform(feature_df)
        pool = Pool(pd.DataFrame(X_scaled, columns=feature_df.columns))
        shap_matrix = cb.get_feature_importance(pool, type='ShapValues')
        shap_vals = shap_matrix[0][:-1]  # last col is expected value baseline
        pairs = sorted(
            zip(list(feature_df.columns), shap_vals),
            key=lambda x: abs(x[1]),
            reverse=True,
        )[:n]
        return [
            {
                "feature":   feat,
                "direction": "up" if val > 0 else "down",
                "impact":    round(abs(float(val)), 4),
            }
            for feat, val in pairs
        ]
    except Exception:
        return []


def predict_campaign_payload(payload: dict, source: str = "api") -> dict:
    ensure_models_loaded()
    data = CampaignInput(**payload)

    feature_df, insights = build_features(data.model_dump(), ml.pipeline_artifacts)
    prob_success  = float(ml.clf_model.predict_proba(feature_df)[0][1])
    shap_factors  = _get_top_shap_factors(ml.clf_model, feature_df)

    _log_prediction(data, prob_success, source)

    comp_pct = insights["competition_pct"]
    return {
        "success": True,
        "prediction": {
            "probability_percentage": round(prob_success * 100, 2),
            "is_viable": prob_success > 0.5,
        },
        "category_stats": {
            "success_rate":    insights["cat_success_rate"],
            "median_goal_usd": insights["median_goal_usd"],
            "total_projects":  insights["cat_project_count"],
            "goal_rank_pct":   insights["goal_rank_in_cat"],
        },
        "competition": {
            "n_competitors": insights["n_competitors"],
            "percentile":    comp_pct,
            "tier": "low" if comp_pct < 0.33 else ("high" if comp_pct > 0.66 else "medium"),
        },
        "shap_factors": shap_factors,
    }


# CANONICAL sentence template — must stay identical to recompute_text_embs.py
def _build_sentence(data: CampaignInput) -> str:
    name_part = f"{data.name}. " if data.name and data.name.strip() else ""
    main_cat  = data.main_category or data.category
    return (
        f"{name_part}A {main_cat} Kickstarter project in the {data.category} subcategory, "
        f"with a ${data.goal_usd:,.0f} funding goal and a {data.duration_days}-day campaign."
    )


def _build_query_vec(data: CampaignInput) -> str:
    vec = ml.embedder.encode([_build_sentence(data)])[0].tolist()
    return "[" + ",".join(f"{x:.6f}" for x in vec) + "]"


def _score(row: tuple, category: str) -> dict:
    p_id, p_name, p_cat, p_goal, p_dur, p_state, sim = row
    cat_match = 1.0 if p_cat == category else 0.0
    prior_val = ml.category_prior.get(p_cat, 0.0)
    total = (W_SIM * sim) + (W_CAT * cat_match) + (W_PRIOR * prior_val)
    return {
        "project_id":       p_id,
        "name":             p_name,
        "category":         p_cat,
        "goal_usd":         p_goal,
        "duration_days":    p_dur,
        "state":            "Successful" if p_state == 1 else "Failed",
        "similarity_score": round(total, 4),
    }


def recommend_campaign_payload(payload: dict, top_k: int = 3) -> dict:
    ensure_models_loaded()
    data      = CampaignInput(**payload)
    query_vec = _build_query_vec(data)

    conn = get_db_connection()
    cur  = conn.cursor()
    cur.execute(
        """
        SELECT project_id, name, category, goal_usd, duration_days, state_binary,
               1 - (text_embedding <=> %s::vector) AS similarity
        FROM   projects
        ORDER  BY text_embedding <=> %s::vector
        LIMIT  100;
        """,
        (query_vec, query_vec),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    scored   = [_score(row, data.category) for row in rows]
    top_list = sorted(scored, key=lambda x: x["similarity_score"], reverse=True)[:top_k]

    return {
        "success":           True,
        "target_category":   data.category,
        "recommended_cases": top_list,
    }
