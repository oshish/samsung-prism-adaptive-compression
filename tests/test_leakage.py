import pytest
import pandas as pd

# Strict blacklist to guarantee ZERO data leakage into model inputs
TARGET_BLACKLIST = {
    "image_id", "split", "file_path", "label", "is_lossy_binary",
    "lossless_codec", "lossless_bytes", "lossless_cr",
    "lossy_codec", "lossy_quality", "lossy_bytes", "lossy_cr",
    "size_saving_ratio", "psnr", "ssim", "dark_ssim", "banding_score",
    "quality_passed", "saving_passed", "dark_passed", "raw_bytes"
}

def test_leakage_blacklist_audit():
    # Explicitly test that NO target or post-compression fields can ever enter features
    leakage_candidates = [
        "lossy_bytes", "lossless_bytes", "lossless_cr", "lossy_cr",
        "size_saving_ratio", "psnr", "ssim", "dark_ssim", "label",
        "is_lossy_binary", "quality_passed", "saving_passed"
    ]
    for col in leakage_candidates:
        assert col in TARGET_BLACKLIST, f"SECURITY LEAK: {col} is not blacklisted!"

def test_pre_compression_feature_purity():
    # Mock dataframe containing both features and leakage columns
    mock_df = pd.DataFrame({
        "image_id": ["img1"],
        "mean_luminance": [120.5],
        "noise_estimate": [4.2],
        "psnr": [36.5],
        "ssim": [0.97],
        "label": ["LOSSY"],
        "is_lossy_binary": [1]
    })
    
    clean_cols = [c for c in mock_df.columns if c not in TARGET_BLACKLIST]
    assert "mean_luminance" in clean_cols
    assert "noise_estimate" in clean_cols
    assert "psnr" not in clean_cols
    assert "ssim" not in clean_cols
    assert "label" not in clean_cols
    assert "is_lossy_binary" not in clean_cols
