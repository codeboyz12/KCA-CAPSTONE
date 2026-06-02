from dataclasses import dataclass, field
from typing import Any


@dataclass
class MLModels:
    clf_model:         Any  = None  # v2 classifier (LightGBM/CatBoost pipeline)
    pipeline_artifacts: Any = None  # preprocessing artifacts dict
    embedder:          Any  = None  # SentenceTransformer for recommend
    scaler:            Any  = None  # structural scaler for recommend
    category_prior:    dict = field(default_factory=dict)
    resources_loaded:  bool = False


ml = MLModels()
