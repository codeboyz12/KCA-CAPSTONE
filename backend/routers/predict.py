from fastapi import APIRouter, HTTPException
import pandas as pd
from schemas.campaign import CampaignInput
from ml.state import ml

router = APIRouter(prefix="/api/v1", tags=["Prediction"])

@router.post("/predict")
def predict_campaign(data: CampaignInput):
    try:
        cat_enc  = ml.encoder.transform([data.category])[0]
        input_df = pd.DataFrame(
            [[cat_enc, data.goal_usd, data.duration_days, data.launch_month]],
            columns=["category_encoded", "goal_usd", "duration_days", "launch_month"],
        )

        prob_success     = float(ml.clf_model.predict_proba(input_df)[0][1])
        expected_pledged = float(ml.reg_model.predict(input_df)[0])

        return {
            "success": True,
            "prediction": {
                "probability_percentage": round(prob_success * 100, 2),
                "expected_pledged_usd":   round(expected_pledged, 2),
                "is_viable":              prob_success > 0.5,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))