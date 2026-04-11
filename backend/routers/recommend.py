from fastapi import APIRouter, HTTPException
from schemas.campaign import CampaignInput
from ml.state import ml
from db.session import get_db_connection

router = APIRouter(prefix="/api/v1", tags=["Recommendation"])

W_TEXT, W_CAT, W_STRUCT, W_PRIOR = 0.3, 0.2, 0.3, 0.2

def _build_vectors(data: CampaignInput) -> tuple[str, str]:
    user_text  = f"A {data.category} project needing ${data.goal_usd} in {data.duration_days} days."
    text_emb   = ml.embedder.encode([user_text])[0].tolist()
    struct_emb = ml.scaler.transform([[data.goal_usd, data.duration_days]])[0].tolist()
    to_pg      = lambda v: "[" + ",".join(map(str, v)) + "]"
    return to_pg(text_emb), to_pg(struct_emb)

def _score(row: tuple, category: str) -> dict:
    p_id, p_name, p_cat, p_goal, p_dur, p_state, text_sim, struct_sim = row
    cat_match = 1.0 if p_cat == category else 0.0
    prior_val = ml.category_prior.get(p_cat, 0.0)
    total     = (W_TEXT   * text_sim)  + (W_CAT    * cat_match) + \
                (W_STRUCT * struct_sim) + (W_PRIOR  * prior_val)
    return {
        "project_id":       p_id,
        "name":             p_name,
        "category":         p_cat,
        "goal_usd":         p_goal,
        "duration_days":    p_dur,
        "state":            "Successful" if p_state == 1 else "Failed",
        "similarity_score": round(total, 4),
    }

@router.post("/recommend")
def get_similar_projects(data: CampaignInput, top_k: int = 3):
    try:
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
        cur  = conn.cursor()
        cur.execute(query, (text_vec, struct_vec, text_vec))
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))