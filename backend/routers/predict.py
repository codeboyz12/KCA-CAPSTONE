from fastapi import APIRouter, HTTPException, Query

from schemas.campaign import CampaignInput
from ml.service import predict_campaign_payload
from tasks.ml_tasks import predict_campaign_task

router = APIRouter(prefix="/api/v1", tags=["Prediction"])

@router.post("/predict")
def predict_campaign(data: CampaignInput, async_mode: bool = Query(False)):
    try:
        payload = data.model_dump()

        if async_mode:
            task = predict_campaign_task.delay(payload)
            return {
                "success": True,
                "task_id": task.id,
                "status": "PENDING",
                "status_endpoint": f"/api/v1/jobs/{task.id}",
            }

        return predict_campaign_payload(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))