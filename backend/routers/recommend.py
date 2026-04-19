from fastapi import APIRouter, HTTPException, Query

from schemas.campaign import CampaignInput
from ml.service import recommend_campaign_payload
from tasks.ml_tasks import recommend_campaign_task

router = APIRouter(prefix="/api/v1", tags=["Recommendation"])

@router.post("/recommend")
def get_similar_projects(
    data: CampaignInput,
    top_k: int = 3,
    async_mode: bool = Query(False),
):
    try:
        payload = data.model_dump()

        if async_mode:
            task = recommend_campaign_task.delay(payload, top_k)
            return {
                "success": True,
                "task_id": task.id,
                "status": "PENDING",
                "status_endpoint": f"/api/v1/jobs/{task.id}",
            }

        return recommend_campaign_payload(payload, top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))