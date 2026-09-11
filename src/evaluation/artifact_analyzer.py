import numpy as np
from scipy import ndimage
from typing import Dict
from skimage.metrics import structural_similarity as ssim_fn
from ..preprocessing.color_space import get_luminance
from ..preprocessing.image_loader import validate_image

def calculate_dark_metrics(
    orig: np.ndarray,
    comp: np.ndarray,
    dark_cutoff: float = 40.0
) -> Dict[str, float]:
    """
    Calculates localized MSE, PSNR, and SSIM strictly over low-luminance (dark) regions.
    Protects against severe DCT blocking and contouring in shadows.
    """
    validate_image(orig)
    validate_image(comp)
    
    Y_orig = get_luminance(orig)
    dark_mask = Y_orig < dark_cutoff
    dark_pixel_count = int(np.count_nonzero(dark_mask))
    
    if dark_pixel_count < 50:
        # Insufficient dark pixels to evaluate dark artifact
        return {
            "dark_pixel_count": dark_pixel_count,
            "dark_mse": 0.0,
            "dark_psnr": 100.0,
            "dark_ssim": 1.0
        }
        
    diff = orig.astype(np.float64) - comp.astype(np.float64)
    # Masked MSE across 3 channels where dark_mask is True
    masked_diff = diff[dark_mask]
    dark_mse = float(np.mean(masked_diff ** 2))
    
    if dark_mse < 1e-10:
        dark_psnr = 100.0
    else:
        dark_psnr = float(10.0 * np.log10((255.0 ** 2) / dark_mse))
        
    # Local SSIM map
    _, ssim_map = ssim_fn(
        orig,
        comp,
        channel_axis=2,
        data_range=255.0,
        full=True
    )
    # Mean SSIM in dark region
    dark_ssim = float(np.mean(ssim_map[dark_mask]))
    
    return {
        "dark_pixel_count": dark_pixel_count,
        "dark_mse": dark_mse,
        "dark_psnr": dark_psnr,
        "dark_ssim": dark_ssim
    }

def detect_banding_score(comp_img: np.ndarray) -> float:
    """
    Quantifies false-contouring / banding in smooth gradient regions.
    Under heavy quantization, smooth continuous gradients turn into staircase plateaus
    (high proportion of exact zero-gradient pixels directly adjacent to step edges).
    Returns a normalized banding risk score in [0.0, 1.0].
    """
    Y = get_luminance(comp_img)
    # Compute horizontal and vertical gradients
    gx = np.abs(ndimage.sobel(Y, axis=1, mode="reflect"))
    gy = np.abs(ndimage.sobel(Y, axis=0, mode="reflect"))
    grad = np.hypot(gx, gy)
    
    # Identify smooth areas (gradient < 15)
    smooth_mask = grad < 15.0
    if np.count_nonzero(smooth_mask) < 200:
        return 0.0
        
    # In perfectly smooth gradients, grad is small but strictly > 0.
    # In banded/quantized steps, grad is identically 0 on steps, with sudden jumps.
    zero_grad_in_smooth = np.count_nonzero(grad[smooth_mask] < 0.5)
    banding_ratio = float(zero_grad_in_smooth / max(1, np.count_nonzero(smooth_mask)))
    return float(np.clip(banding_ratio, 0.0, 1.0))

def calculate_edge_preservation(orig: np.ndarray, comp: np.ndarray) -> float:
    """
    Measures gradient energy retention across strong edges.
    Ratio = Sum(Gradient_comp) / Sum(Gradient_orig).
    < 1.0: blurring/detail loss.
    > 1.0: ringing/high-frequency noise amplification.
    """
    Y_orig = get_luminance(orig)
    Y_comp = get_luminance(comp)
    
    grad_orig = np.hypot(
        ndimage.sobel(Y_orig, axis=1, mode="reflect"),
        ndimage.sobel(Y_orig, axis=0, mode="reflect")
    )
    grad_comp = np.hypot(
        ndimage.sobel(Y_comp, axis=1, mode="reflect"),
        ndimage.sobel(Y_comp, axis=0, mode="reflect")
    )
    
    sum_orig = float(np.sum(grad_orig))
    sum_comp = float(np.sum(grad_comp))
    
    if sum_orig < 1e-6:
        return 1.0
    return float(sum_comp / sum_orig)
