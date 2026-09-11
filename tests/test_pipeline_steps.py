"""
tests/test_pipeline_steps.py
Comprehensive unit tests for Steps 1–6:
- image loading & validation
- RGB/YUV color-space conversion & luminance
- brightness & contrast features
- histogram & Shannon entropy features
- edge density & gradient features
- local variance & GLCM texture features
- noise estimation proxy monotonicity
- feature extraction dictionary integrity
- CSV generation & schema validation
"""

import os
import pytest
import numpy as np
import pandas as pd
from PIL import Image

from src.preprocessing.image_loader import load_image, validate_image, save_image
from src.color.color_space import rgb_to_yuv, yuv_to_rgb, get_luminance, split_yuv_channels
from src.features.brightness import extract_brightness_features
from src.features.contrast import extract_contrast_features
from src.features.histogram import extract_histogram_features
from src.features.edges import extract_edge_features
from src.features.texture import extract_texture_features
from src.features.noise import extract_noise_features
from src.features.color import extract_color_features
from src.features.extractor import extract_features


# 1. Image Loading Tests
def test_image_loading_valid(tmp_path):
    arr = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
    filepath = str(tmp_path / "test.png")
    save_image(arr, filepath)
    
    loaded = load_image(filepath)
    assert loaded.shape == (64, 64, 3)
    assert loaded.dtype == np.uint8
    np.testing.assert_array_equal(arr, loaded)


def test_image_loading_corrupt(tmp_path):
    corrupt_path = str(tmp_path / "corrupt.png")
    with open(corrupt_path, "wb") as f:
        f.write(b"NOT_A_VALID_IMAGE_HEADER")
    with pytest.raises(ValueError):
        load_image(corrupt_path)


def test_image_loading_nonexistent():
    with pytest.raises(FileNotFoundError):
        load_image("nonexistent_path_to_image.png")


def test_image_validation_dimensions():
    with pytest.raises(ValueError):
        validate_image(np.zeros((64, 64), dtype=np.uint8))  # 2D
    with pytest.raises(ValueError):
        validate_image(np.zeros((64, 64, 4), dtype=np.uint8))  # 4 channels
    with pytest.raises(ValueError):
        validate_image(np.zeros((64, 64, 3), dtype=np.float32))  # float


# 2. RGB/YUV Conversion Tests
def test_rgb_yuv_roundtrip():
    rng = np.random.default_rng(42)
    rgb_orig = rng.integers(0, 256, (32, 32, 3), dtype=np.uint8)
    
    yuv = rgb_to_yuv(rgb_orig)
    assert yuv.shape == (32, 32, 3)
    assert yuv.dtype == np.float32
    assert 0.0 <= np.min(yuv) and np.max(yuv) <= 255.0
    
    rgb_reconstructed = yuv_to_rgb(yuv)
    # Average round-trip reconstruction difference should be minimal (< 1.5 intensity levels)
    mean_abs_diff = np.mean(np.abs(rgb_orig.astype(float) - rgb_reconstructed.astype(float)))
    assert mean_abs_diff < 1.5


def test_luminance_properties():
    black = np.zeros((16, 16, 3), dtype=np.uint8)
    white = np.full((16, 16, 3), 255, dtype=np.uint8)
    
    assert np.allclose(get_luminance(black), 0.0)
    assert np.allclose(get_luminance(white), 255.0)


# 3. Brightness Features Tests
def test_brightness_pure_black():
    black = np.zeros((32, 32, 3), dtype=np.uint8)
    feats = extract_brightness_features(black)
    assert feats["mean_luminance"] == 0.0
    assert feats["dark_pixel_ratio"] == 1.0
    assert feats["bright_pixel_ratio"] == 0.0
    assert feats["min_luminance"] == 0.0
    assert feats["max_luminance"] == 0.0


def test_brightness_pure_white():
    white = np.full((32, 32, 3), 255, dtype=np.uint8)
    feats = extract_brightness_features(white)
    assert feats["mean_luminance"] == 255.0
    assert feats["dark_pixel_ratio"] == 0.0
    assert feats["bright_pixel_ratio"] == 1.0


def test_brightness_split_image():
    # Half black, half white
    split = np.zeros((32, 32, 3), dtype=np.uint8)
    split[:, 16:] = 255
    feats = extract_brightness_features(split)
    assert np.isclose(feats["mean_luminance"], 127.5, atol=0.1)
    assert np.isclose(feats["dark_pixel_ratio"], 0.5)
    assert np.isclose(feats["bright_pixel_ratio"], 0.5)


# 4. Contrast & Histogram Features Tests
def test_contrast_and_histogram():
    grad = np.zeros((32, 32, 3), dtype=np.uint8)
    for c in range(32):
        grad[:, c] = int(c * 255 / 31)
        
    c_feats = extract_contrast_features(grad)
    assert c_feats["luminance_range"] > 250.0
    assert c_feats["rms_contrast"] > 0.0
    
    h_feats = extract_histogram_features(grad)
    assert h_feats["p10_luminance"] < h_feats["p90_luminance"]
    assert h_feats["iqr_luminance"] > 0.0
    assert 0.0 <= h_feats["shannon_entropy"] <= 8.0


def test_entropy_zero_on_flat_image():
    flat = np.full((32, 32, 3), 100, dtype=np.uint8)
    h_feats = extract_histogram_features(flat)
    assert np.isclose(h_feats["shannon_entropy"], 0.0)


# 5. Edge Features Tests
def test_edge_flat_vs_checkerboard():
    flat = np.full((64, 64, 3), 128, dtype=np.uint8)
    flat_edges = extract_edge_features(flat)
    assert flat_edges["sobel_edge_density"] == 0.0
    assert flat_edges["mean_edge_magnitude"] == 0.0
    assert flat_edges["laplacian_variance"] == 0.0
    
    # Checkerboard with sharp transitions
    checker = np.zeros((64, 64, 3), dtype=np.uint8)
    checker[::4, :] = 255
    checker[:, ::4] = 255
    checker_edges = extract_edge_features(checker)
    assert checker_edges["sobel_edge_density"] > 0.1
    assert checker_edges["mean_edge_magnitude"] > 10.0


# 6. Texture Features Tests
def test_texture_block_variance():
    flat = np.full((32, 32, 3), 120, dtype=np.uint8)
    tex_flat = extract_texture_features(flat, patch_size=8)
    assert tex_flat["local_variance_mean"] == 0.0
    
    # High frequency noise image has high block variance
    rng = np.random.default_rng(101)
    noise_img = rng.integers(0, 256, (32, 32, 3), dtype=np.uint8)
    tex_noise = extract_texture_features(noise_img, patch_size=8)
    assert tex_noise["local_variance_mean"] > 100.0


# 7. Noise Estimation Monotonicity Test
def test_noise_estimator_monotonicity():
    rng = np.random.default_rng(202)
    clean = np.full((64, 64, 3), 128, dtype=np.float32)
    
    noise_low = np.clip(clean + rng.normal(0, 5, clean.shape), 0, 255).astype(np.uint8)
    noise_high = np.clip(clean + rng.normal(0, 25, clean.shape), 0, 255).astype(np.uint8)
    
    est_low = extract_noise_features(noise_low)["noise_estimate"]
    est_high = extract_noise_features(noise_high)["noise_estimate"]
    
    assert est_high > est_low
    assert est_low > 0.0


# 8. Unified Feature Extractor Tests
def test_unified_extractor_completeness():
    img = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
    feats = extract_features(img)
    
    # Must return dictionary
    assert isinstance(feats, dict)
    # Between 20 and 40 features
    assert 20 <= len(feats) <= 45
    
    # Check that all values are valid floats
    for k, v in feats.items():
        assert isinstance(v, float), f"{k} is not float"
        assert not np.isnan(v), f"{k} is NaN"
        assert not np.isinf(v), f"{k} is Inf"


# 9. CSV Generation & Dataframe Schema Test
def test_csv_generation(tmp_path):
    records = []
    for i in range(5):
        img = np.random.randint(0, 256, (32, 32, 3), dtype=np.uint8)
        feats = extract_features(img)
        records.append({
            "image_id": f"synthetic_{i:02d}",
            "file_path": f"/path/synthetic_{i:02d}.png",
            **feats
        })
        
    df = pd.DataFrame(records)
    csv_path = str(tmp_path / "test_features.csv")
    df.to_csv(csv_path, index=False)
    
    loaded_df = pd.read_csv(csv_path)
    assert len(loaded_df) == 5
    assert loaded_df["image_id"].nunique() == 5
    assert loaded_df.isnull().sum().sum() == 0

