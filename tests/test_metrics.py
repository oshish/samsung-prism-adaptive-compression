import pytest
import numpy as np

from src.evaluation.metrics import calculate_mse, calculate_psnr, calculate_ssim
from src.evaluation.artifact_analyzer import calculate_dark_metrics, detect_banding_score

def test_metrics_identical_images():
    img = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
    assert calculate_mse(img, img) == 0.0
    assert calculate_psnr(img, img) == float("inf")
    assert calculate_ssim(img, img) == 1.0

def test_metrics_perturbed_images():
    img1 = np.full((64, 64, 3), 128, dtype=np.uint8)
    img2 = np.full((64, 64, 3), 138, dtype=np.uint8)
    
    mse = calculate_mse(img1, img2)
    assert mse == 100.0
    
    psnr = calculate_psnr(img1, img2)
    assert psnr < 100.0
    
    ssim = calculate_ssim(img1, img2)
    assert ssim < 1.0

def test_dark_metrics():
    # Image with half dark pixels and half bright pixels
    orig = np.zeros((50, 50, 3), dtype=np.uint8)
    orig[:25] = 20 # dark (< 40)
    orig[25:] = 200 # bright
    
    comp = orig.copy()
    comp[:25] = 25 # add error in dark region
    
    dark_res = calculate_dark_metrics(orig, comp, dark_cutoff=40.0)
    assert dark_res["dark_pixel_count"] == 25 * 50
    assert dark_res["dark_mse"] == 25.0
    assert dark_res["dark_ssim"] < 1.0
