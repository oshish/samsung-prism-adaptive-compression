import pytest
import numpy as np
import pandas as pd
from src.compression.benchmark import run_codec_suite, benchmark_compression
from src.dataset.labeler import generate_ground_truth_label
from src.evaluation.metrics import evaluate_quality, calculate_mse, calculate_psnr, calculate_ssim
from src.evaluation.artifact_analyzer import calculate_dark_metrics, detect_banding_score, calculate_edge_preservation
from src.evaluation.system_evaluator import evaluate_system_impact
from src.models.ml_baselines import train_baseline_models
from src.models.model_evaluator import evaluate_classifier

def test_run_codec_suite_output():
    img = np.zeros((64, 64, 3), dtype=np.uint8)
    img[:, :, 0] = np.linspace(0, 255, 64, dtype=np.uint8)
    
    results = run_codec_suite(
        img,
        lossless_codecs=["png", "webp_lossless"],
        lossy_codecs=["jpeg"],
        lossy_qualities=[75, 85]
    )
    
    assert len(results) == 4
    codecs = [r.codec for r in results]
    assert "png" in codecs
    assert "webp_lossless" in codecs
    assert "jpeg" in codecs
    
    for r in results:
        assert r.compressed_bytes > 0
        assert r.compression_ratio > 0.0
        assert r.encode_time_ms >= 0.0
        assert r.decode_time_ms >= 0.0
        assert r.decompressed_img.shape == (64, 64, 3)

def test_label_generation_decision_boundaries():
    img_white = np.full((64, 64, 3), 240, dtype=np.uint8)
    label_white = generate_ground_truth_label(img_white)
    assert label_white["label"] in ("LOSSY", "LOSSLESS")
    assert "psnr" in label_white
    assert "ssim" in label_white
    assert "dark_ssim" in label_white
    assert "size_saving_ratio" in label_white
    
    img_dark = np.random.randint(0, 25, (64, 64, 3), dtype=np.uint8)
    label_dark = generate_ground_truth_label(img_dark)
    assert "label" in label_dark

def test_system_evaluator_tradeoff():
    test_meta = pd.DataFrame([
        {
            "image_id": "img1",
            "raw_bytes": 10000,
            "lossless_bytes": 5000,
            "lossy_bytes": 1000,
            "ssim": 0.98,
            "psnr": 38.0,
            "dark_ssim": 0.96
        },
        {
            "image_id": "img2",
            "raw_bytes": 10000,
            "lossless_bytes": 5000,
            "lossy_bytes": 2000,
            "ssim": 0.90,
            "psnr": 30.0,
            "dark_ssim": 0.85
        }
    ])
    
    preds = {
        "always_lossless_model": np.array([0, 0]),
        "always_lossy_model": np.array([1, 1]),
        "smart_model": np.array([1, 0])
    }
    
    eval_res = evaluate_system_impact(
        test_metadata=test_meta,
        predictions=preds,
        ssim_threshold=0.94,
        psnr_threshold=33.0,
        dark_ssim_threshold=0.90
    )
    
    strats = eval_res["strategies"]
    assert "always_lossless" in strats
    assert "always_lossy" in strats
    assert "smart_model" in strats
    
    assert strats["smart_model"]["critical_failures"] == 0
    assert strats["always_lossy"]["critical_failures"] == 1
    assert strats["smart_model"]["saving_vs_lossless_pct"] > 0.0

def test_edge_preservation_bounds():
    img = np.zeros((64, 64, 3), dtype=np.uint8)
    img[20:40, 20:40] = 200
    
    ep_ident = calculate_edge_preservation(img, img)
    assert pytest.approx(ep_ident, abs=1e-3) == 1.0
    
    from scipy.ndimage import gaussian_filter
    blurred = gaussian_filter(img.astype(float), sigma=2.0).astype(np.uint8)
    ep_blurred = calculate_edge_preservation(img, blurred)
    assert ep_blurred < 1.0
