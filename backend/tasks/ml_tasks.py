import logging

from celery_app import celery_app
from ml.service import predict_campaign_payload, recommend_campaign_payload
from core import cache

logger = logging.getLogger("kca.predict")


@celery_app.task(name="tasks.predict_campaign")
def predict_campaign_task(payload: dict) -> dict:
    key = cache.make_key(payload)
    cached = cache.get(key)

    if cached:
        logger.info(
            "PREDICT [HIT]  key=%s  category=%s  goal=%s  duration=%s  (async)",
            key[-8:], payload.get("category"), payload.get("goal_usd"), payload.get("duration_days"),
        )
        return cached

    logger.info(
        "PREDICT [MISS] key=%s  category=%s  goal=%s  duration=%s — executing inference (async)",
        key[-8:], payload.get("category"), payload.get("goal_usd"), payload.get("duration_days"),
    )
    result = predict_campaign_payload(payload)
    cache.set(key, result)
    return result


@celery_app.task(name="tasks.recommend_campaign")
def recommend_campaign_task(payload: dict, top_k: int = 3) -> dict:
    return recommend_campaign_payload(payload, top_k)
