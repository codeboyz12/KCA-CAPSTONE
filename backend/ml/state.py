from dataclasses import dataclass, field
from typing import Any


@dataclass
class MLModels:
    clf_model:          Any  = None  # v2 classifier (CatBoost pipeline)
    pipeline_artifacts: Any  = None  # preprocessing artifacts dict
    embedder:           Any  = None  # SentenceTransformer — shared by /search + /recommend
    category_prior:     dict = field(default_factory=dict)
    resources_loaded:   bool = False


ml = MLModels()
