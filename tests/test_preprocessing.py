import pytest
import numpy as np
import tempfile
import os
from PIL import Image

from src.preprocessing.image_loader import load_image, validate_image, save_image, get_image_metadata
from src.preprocessing.color_space import rgb_to_yuv, yuv_to_rgb, get_luminance

def test_validate_image_valid():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    validate_image(img) # Should not raise

def test_validate_image_invalid():
    with pytest.raises(ValueError):
        validate_image(np.zeros((100, 100), dtype=np.uint8)) # 2D
    with pytest.raises(ValueError):
        validate_image(np.zeros((100, 100, 4), dtype=np.uint8)) # 4 channels
    with pytest.raises(ValueError):
        validate_image(np.zeros((100, 100, 3), dtype=np.float32)) # wrong dtype
    with pytest.raises(ValueError):
        validate_image(np.zeros((0, 100, 3), dtype=np.uint8)) # zero dimension

def test_save_and_load_image():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_path = os.path.join(tmpdir, "test.png")
        original = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
        save_image(original, test_path)
        
        loaded = load_image(test_path)
        assert np.array_equal(original, loaded)
        
        meta = get_image_metadata(loaded)
        assert meta["height"] == 64
        assert meta["width"] == 64
        assert meta["channels"] == 3
        assert meta["raw_bytes"] == 64 * 64 * 3

def test_load_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        load_image("nonexistent_image_xyz_123.png")

def test_rgb_yuv_roundtrip():
    # Test RGB -> YUV -> RGB roundtrip tolerance
    rng = np.random.default_rng(42)
    rgb = rng.integers(0, 256, (50, 50, 3), dtype=np.uint8)
    
    yuv = rgb_to_yuv(rgb, standard="BT601")
    rgb_recon = yuv_to_rgb(yuv, standard="BT601")
    
    # Integer roundoff error should not exceed 2 gray levels
    max_err = np.max(np.abs(rgb.astype(int) - rgb_recon.astype(int)))
    assert max_err <= 2

def test_luminance_range():
    rgb = np.full((30, 30, 3), 128, dtype=np.uint8)
    lum = get_luminance(rgb)
    assert lum.shape == (30, 30)
    assert np.allclose(lum, 128.0, atol=1.0)
