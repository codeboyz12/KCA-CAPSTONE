from fastapi import APIRouter, HTTPException
from db.session import get_db_connection

router = APIRouter(prefix="/api/v1", tags=["Stats"])


@router.get("/stats/categories")
def get_category_stats():
    """Return pre-computed category statistics from the materialized view."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT category, total_projects, successful_count,
                   success_rate, avg_goal_usd, median_goal_usd, avg_duration_days
            FROM category_stats
            ORDER BY total_projects DESC;
            """
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return {
            "success": True,
            "data": [
                {
                    "category":        row[0],
                    "total_projects":  row[1],
                    "successful_count": row[2],
                    "success_rate":    float(row[3]),
                    "avg_goal_usd":    float(row[4]),
                    "median_goal_usd": float(row[5]),
                    "avg_duration_days": float(row[6]),
                }
                for row in rows
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/predictions")
def get_prediction_log(limit: int = 50):
    """Return recent prediction log entries for drift monitoring."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT log_id, requested_at, category, goal_usd,
                   duration_days, prob_success, is_viable, source
            FROM prediction_log
            ORDER BY requested_at DESC
            LIMIT %s;
            """,
            (limit,),
        )
        rows = cur.fetchall()

        cur.execute("SELECT COUNT(*) FROM prediction_log;")
        total = cur.fetchone()[0]

        cur.close()
        conn.close()

        return {
            "success": True,
            "total_predictions": total,
            "data": [
                {
                    "log_id":        row[0],
                    "requested_at":  row[1].isoformat(),
                    "category":      row[2],
                    "goal_usd":      row[3],
                    "duration_days": row[4],
                    "prob_success":  row[5],
                    "is_viable":     row[6],
                    "source":        row[7],
                }
                for row in rows
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
