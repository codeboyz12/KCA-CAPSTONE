from fastapi import APIRouter, HTTPException
from db.session import get_db_connection

router = APIRouter(prefix="/api/v1", tags=["Projects"])

@router.get("/projects")
def get_all_projects(page: int = 1, limit: int = 12):
    try:
        offset = (page - 1) * limit
        conn   = get_db_connection()
        cur    = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM projects;")
        total_items = cur.fetchone()[0]
        total_pages = (total_items + limit - 1) // limit

        cur.execute(
            """
            SELECT project_id, name, category, goal_usd, duration_days, state_binary
            FROM projects
            ORDER BY project_id
            LIMIT %s OFFSET %s;
            """,
            (limit, offset),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        projects = [
            {
                "id":       row[0],
                "name":     row[1],
                "category": row[2],
                "goal":     row[3],
                "duration": row[4],
                "state":    "successful" if row[5] == 1 else "failed",
            }
            for row in rows
        ]

        return {
            "success": True,
            "data":    projects,
            "pagination": {
                "current_page": page,
                "total_pages":  total_pages,
                "total_items":  total_items,
                "limit":        limit,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))