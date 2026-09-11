import numpy as np
import pandas as pd
from typing import Dict, Any, List

class MajorityClassBaseline:
    """
    Baseline that predicts the majority class observed in the training set.
    """
    def __init__(self):
        self.majority_class: str = "LOSSY"
        self.majority_binary: int = 1
        
    def fit(self, X: pd.DataFrame, y: pd.Series) -> "MajorityClassBaseline":
        value_counts = y.value_counts()
        self.majority_class = str(value_counts.index[0])
        self.majority_binary = 1 if self.majority_class == "LOSSY" else 0
        return self
        
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return np.full(len(X), self.majority_binary, dtype=int)
        
    def predict_labels(self, X: pd.DataFrame) -> List[str]:
        return [self.majority_class] * len(X)

class RuleBasedBaseline:
    """
    Intuition-driven rule-based heuristic baseline:
    Predicts LOSSY for images that are reasonably bright, not dominated by dark regions,
    and have moderate to low noise and texture complexity.
    """
    def __init__(
        self,
        min_luminance: float = 65.0,
        max_dark_ratio: float = 0.35,
        max_noise: float = 12.0,
        max_laplacian: float = 800.0
    ):
        self.min_luminance = min_luminance
        self.max_dark_ratio = max_dark_ratio
        self.max_noise = max_noise
        self.max_laplacian = max_laplacian
        
    def fit(self, X: pd.DataFrame, y: pd.Series) -> "RuleBasedBaseline":
        # Rule-based model uses fixed domain heuristic
        return self
        
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        preds = []
        for _, row in X.iterrows():
            lum = row.get("mean_luminance", 128.0)
            dark_ratio = row.get("dark_pixel_ratio", 0.0)
            noise = row.get("noise_estimate", 0.0)
            laplacian = row.get("laplacian_variance", 100.0)
            
            # Rule conditions
            is_bright_enough = lum >= self.min_luminance
            not_too_dark = dark_ratio <= self.max_dark_ratio
            low_noise = noise <= self.max_noise
            not_extreme_texture = laplacian <= self.max_laplacian
            
            if is_bright_enough and not_too_dark and low_noise and not_extreme_texture:
                preds.append(1) # LOSSY
            else:
                preds.append(0) # LOSSLESS
                
        return np.array(preds, dtype=int)
        
    def predict_labels(self, X: pd.DataFrame) -> List[str]:
        preds = self.predict(X)
        return ["LOSSY" if p == 1 else "LOSSLESS" for p in preds]
