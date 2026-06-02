"""Shared encoder classes used by both train.py and inference."""

import numpy as np
import pandas as pd


class BinaryEncoder:
    """Minimal binary encoder for a single categorical column."""

    def __init__(self, col: str):
        self.col = col
        self.categories_: list = []
        self.n_bits_: int = 0

    def fit(self, series: pd.Series) -> "BinaryEncoder":
        self.categories_ = sorted(series.dropna().unique().tolist())
        self.n_bits_ = max(1, int(np.ceil(np.log2(len(self.categories_) + 1))))
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        idx_map = {v: i + 1 for i, v in enumerate(self.categories_)}
        codes = out[self.col].map(idx_map).fillna(0).astype(int).values
        for bit in range(self.n_bits_):
            out[f"{self.col}_{bit}"] = (codes >> bit) & 1
        return out.drop(columns=[self.col])

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self.fit(df[self.col])
        return self.transform(df)
