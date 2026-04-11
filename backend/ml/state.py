from dataclasses import dataclass, field
from typing import Any

@dataclass
class MLModels:
    clf_model:      Any  = None
    reg_model:      Any  = None
    encoder:        Any  = None
    scaler:         Any  = None
    embedder:       Any  = None
    category_prior: dict = field(default_factory=dict)

ml = MLModels()