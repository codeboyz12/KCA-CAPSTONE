from fastapi import APIRouter
from ml.service import ensure_models_loaded
from ml.state import ml

router = APIRouter(prefix="/api/v1", tags=["Metadata"])

@router.get("/metadata")
def get_metadata():
    ensure_models_loaded()
    categories = sorted(ml.pipeline_artifacts["agg_map"]["cat_success_rate"].index.tolist())
    main_categories = sorted({mc for mc, _ in ml.pipeline_artifacts["lag1_map"].keys()})
    return {
        "available_categories": categories,
        "available_main_categories": main_categories,
    }


@router.get("/metadata/main-categories")
def get_main_categories():
    ensure_models_loaded()
    main_categories = sorted({mc for mc, _ in ml.pipeline_artifacts["lag1_map"].keys()})
    return {"main_categories": main_categories}