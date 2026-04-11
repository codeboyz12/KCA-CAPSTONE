from fastapi import APIRouter
from ml.state import ml

router = APIRouter(prefix="/api/v1", tags=["Metadata"])

@router.get("/metadata")
def get_metadata():
    categories = ml.encoder.classes_.tolist()
    return {"available_categories": categories}