import pytest
import numpy as np
import pandas as pd

from src.models.baseline_heuristics import MajorityClassBaseline, RuleBasedBaseline
from src.models.ml_baselines import train_baseline_models
from src.models.model_evaluator import evaluate_classifier

def test_baseline_models_fit_and_predict():
    # Create synthetic dataset
    rng = np.random.default_rng(42)
    n_samples = 20
    X = pd.DataFrame({
        "mean_luminance": rng.uniform(20, 200, n_samples),
        "dark_pixel_ratio": rng.uniform(0, 0.5, n_samples),
        "laplacian_variance": rng.uniform(10, 500, n_samples),
        "noise_estimate": rng.uniform(1, 15, n_samples),
        "shannon_entropy_y": rng.uniform(4, 8, n_samples)
    })
    y = rng.integers(0, 2, n_samples)
    
    models = train_baseline_models(X, y, random_state=42)
    assert "majority" in models
    assert "rule_based" in models
    assert "logistic_regression" in models
    assert "decision_tree" in models
    assert "random_forest" in models
    
    for name, model in models.items():
        preds = model.predict(X)
        assert len(preds) == n_samples
        assert set(np.unique(preds)).issubset({0, 1})
        
        metrics = evaluate_classifier(y, preds)
        assert "accuracy" in metrics
        assert "f1_score" in metrics
        assert "confusion_matrix" in metrics
