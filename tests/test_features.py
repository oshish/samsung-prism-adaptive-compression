import pytest
import numpy as np

from src.features.extractor import extract_features
from src.features.brightness_features import extract_brightness_features
from src.features.edge_features import extract_edge_features
from src.features.noise_features import extract_noise_features

def test_feature_extractor_structure():
    img = np.random.randint(0, 256, (128, 128, 3), dtype=np.uint8)
    feats = extract_features(img)
    
    expected_keys = [
        "mean_luminance", "std_luminance", "dark_pixel_ratio", "bright_pixel_ratio",
        "local_variance_mean", "glcm_contrast", "sobel_edge_density",
        "laplacian_variance", "noise_estimate", "shannon_entropy_y", "colorfulness"
    ]
    for key in expected_keys:
        assert key in feats, f"Missing feature: {key}"
        assert not np.isnan(feats[key]), f"Feature {key} is NaN"
        assert not np.isinf(feats[key]), f"Feature {key} is Inf"

def test_features_pure_black_edge_case():
    black_img = np.zeros((64, 64, 3), dtype=np.uint8)
    feats = extract_features(black_img)
    
    assert feats["mean_luminance"] == 0.0
    assert feats["dark_pixel_ratio"] == 1.0
    assert feats["bright_pixel_ratio"] == 0.0
    assert feats["noise_estimate"] == 0.0
    for v in feats.values():
        assert not np.isnan(v)

def test_features_flat_white_edge_case():
    white_img = np.full((64, 64, 3), 255, dtype=np.uint8)
    feats = extract_features(white_img)
    
    assert feats["mean_luminance"] == 255.0
    assert feats["dark_pixel_ratio"] == 0.0
    assert feats["bright_pixel_ratio"] == 1.0
    assert feats["sobel_edge_density"] == 0.0
    for v in feats.values():
        assert not np.isnan(v)
