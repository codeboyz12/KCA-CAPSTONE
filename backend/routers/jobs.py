from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException

from celery_app import celery_app

router = APIRouter(prefix="/api/v1/jobs", tags=["Jobs"])


@router.get("/{task_id}")
def get_job_status(task_id: str):
    try:
        result = AsyncResult(task_id, app=celery_app)

        response = {
            "task_id": task_id,
            "status": result.status,
            "ready": result.ready(),
            "successful": result.successful() if result.ready() else False,
        }

        if result.ready() and result.successful():
            response["result"] = result.result

        if result.failed():
            response["error"] = str(result.result)

        return response
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
