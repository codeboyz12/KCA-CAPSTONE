from fastapi import APIRouter
from tasks.retrain_task import retrain_model_task

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@router.post("/retrain")
def trigger_retrain():
    task = retrain_model_task.delay()
    return {
        "success": True,
        "message": "Retraining job queued",
        "task_id": task.id,
        "status": "PENDING",
        "status_endpoint": f"/api/v1/jobs/{task.id}",
    }
