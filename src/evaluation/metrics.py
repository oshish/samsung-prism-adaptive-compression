import numpy as np
from typing import Dict, Any
from skimage.metrics import structural_similarity as ssim_fn
from ..preprocessing.image_loader import validate_image

def calculate_mse(orig: np.ndarray, comp: np.ndarray) -> float:
    """
    Computes Mean Squared Error across all pixels and color channels.
    """
    validate_image(orig)
    validate_image(comp)
    if orig.shape != comp.shape:
        raise ValueError(f"Shape mismatch: {orig.shape} vs {comp.shape}")
    diff = orig.astype(np.float64) - comp.astype(np.float64)
    return float(np.mean(diff ** 2))

def calculate_psnr(orig: np.ndarray, comp: np.ndarray, max_val: float = 255.0) -> float:
    """
    Computes Peak Signal-to-Noise Ratio (PSNR) in dB.
    Returns float('inf') for identical images (MSE == 0).
    """
    mse = calculate_mse(orig, comp)
    if mse < 1e-10:
        return float("inf")
    return float(10.0 * np.log10((max_val ** 2) / mse))

def calculate_ssim(orig: np.ndarray, comp: np.ndarray) -> float:
    """
    Computes Structural Similarity Index (SSIM) across RGB channels using standard Gaussian window.
    Range: [-1.0, 1.0], where 1.0 indicates perfect structural identity.
    """
    validate_image(orig)
    validate_image(comp)
    if orig.shape != comp.shape:
        raise ValueError(f"Shape mismatch: {orig.shape} vs {comp.shape}")
    
    score = ssim_fn(
        orig,
        comp,
        channel_axis=2,
        data_range=255.0,
        win_size=11,
        gaussian_weights=True
    )
    return float(score)

def evaluate_quality(orig: np.ndarray, comp: np.ndarray) -> Dict[str, float]:
    """
    Evaluates both PSNR and SSIM between original and compressed frames.
    """
    mse = calculate_mse(orig, comp)
    psnr = calculate_psnr(orig, comp)
    ssim = calculate_ssim(orig, comp)
    return {
        "mse": float(mse),
        "psnr": float(psnr),
        "ssim": float(ssim)
    }

def lpips_feasibility_analysis() -> Dict[str, Any]:
    """
    Documents the technical analysis of Learned Perceptual Image Patch Similarity (LPIPS)
    for mobile/runtime adaptive frame compression vs offline evaluation.
    """
    return {
        "metric_name": "LPIPS (Learned Perceptual Image Patch Similarity)",
        "formulation": "Deep feature distance using pretrained AlexNet / VGG backbone layers",
        "advantages": [
            "Significantly higher correlation with human subjective quality (MOS) on high-frequency textures",
            "Sensitive to perceptual blur, ringing, and GAN/neural generative artifacts"
        ],
        "limitations_for_mobile": [
            "Requires PyTorch / TorchVision and pretrained neural network weights (~50MB - 100MB)",
            "Execution latency is ~50ms to 200ms per 1080p frame on mobile GPU/NPU (100x slower than SSIM)",
            "Incompatible with hard real-time display/camera frame buffer pipelines (< 2ms budget)"
        ],
        "recommendation": (
            "SSIM and PSNR serve as the primary fast quantitative criteria for Milestone 1. "
            "LPIPS is recommended strictly for offline validation and rate-distortion benchmarking in Milestone 2."
        )
    }
