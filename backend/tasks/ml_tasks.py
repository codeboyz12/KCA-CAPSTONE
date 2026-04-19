from celery_app import celery_app
from ml.service import predict_campaign_payload, recommend_campaign_payload


@celery_app.task(name="tasks.predict_campaign")
def predict_campaign_task(payload: dict) -> dict:
    return predict_campaign_payload(payload)


@celery_app.task(name="tasks.recommend_campaign")
def recommend_campaign_task(payload: dict, top_k: int = 3) -> dict:
    return recommend_campaign_payload(payload, top_k)
