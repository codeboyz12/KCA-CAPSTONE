from fastapi import APIRouter, HTTPException
from functools import lru_cache

from ml.state import ml
from db.session import get_db_connection

router = APIRouter(prefix="/api/v1", tags=["Search"])

# Maximum results fetched from the HNSW index per query.
# Paginated in Python — no second COUNT query.
_MAX_RESULTS = 120


@lru_cache(maxsize=256)
def _embed(query: str) -> str:
    """Embed *query* and return a pgvector-compatible string '[x,y,...]'.

    lru_cache means identical queries skip the model entirely after the first call.
    """
    vec = ml.embedder.encode([query])[0]
    return '[' + ','.join(f'{x:.6f}' for x in vec) + ']'


@router.get("/search")
def semantic_search(q: str, page: int = 1, limit: int = 12):
    q = q.strip()
    if not q:
        raise HTTPException(status_code=400, detail="q is required")
    if ml.embedder is None:
        raise HTTPException(status_code=503, detail="Search model not ready")

    vec_str = _embed(q)

    conn = get_db_connection()
    cur  = conn.cursor()

    # Use HNSW index — intentionally omit text_embedding from SELECT
    # to avoid transferring 384 floats per row back to Python.
    cur.execute(
        """
        SELECT project_id, name, category, goal_usd, duration_days, state_binary
        FROM   projects
        ORDER  BY text_embedding <=> %s::vector
        LIMIT  %s;
        """,
        (vec_str, _MAX_RESULTS),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    total_items = len(rows)
    total_pages = max(1, (total_items + limit - 1) // limit)
    offset      = (page - 1) * limit
    page_rows   = rows[offset : offset + limit]

    return {
        "success": True,
        "data": [
            {
                "id":       row[0],
                "name":     row[1],
                "category": row[2],
                "goal":     row[3],
                "duration": row[4],
                "state":    "successful" if row[5] == 1 else "failed",
            }
            for row in page_rows
        ],
        "pagination": {
            "current_page": page,
            "total_pages":  total_pages,
            "total_items":  total_items,
            "limit":        limit,
        },
    }
