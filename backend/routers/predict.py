import logging

from fastapi import APIRouter, HTTPException, Query

from schemas.campaign import CampaignInput
from ml.service import predict_campaign_payload
from tasks.ml_tasks import predict_campaign_task
from core import cache

logger = logging.getLogger("kca.predict")

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

        key = cache.make_key(payload)
        cached = cache.get(key)

        if cached:
            logger.info(
                "PREDICT [HIT]  key=%s  category=%s  goal=%s  duration=%s",
                key[-8:], payload.get("category"), payload.get("goal_usd"), payload.get("duration_days"),
            )
            return cached

        logger.info(
            "PREDICT [MISS] key=%s  category=%s  goal=%s  duration=%s — executing inference",
            key[-8:], payload.get("category"), payload.get("goal_usd"), payload.get("duration_days"),
        )
        result = predict_campaign_payload(payload)
        cache.set(key, result)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))