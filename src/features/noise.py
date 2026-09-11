"""
src/features/noise.py
Extracts noise estimation proxies: Immerkaer fast Laplacian mask and dark chroma variance.

Methodology:
1. Immerkaer Fast Noise Estimator (Immerkaer, 1996: "Fast Noise Variance Estimation"):
   Applies a discrete 3x3 pseudo-Laplacian mask:
       N = [  1  -2   1 ]
           [ -2   4  -2 ]
           [  1  -2   1 ]
   Under the assumption of zero-mean additive Gaussian noise, the standard deviation is estimated as:
       sigma_n = sqrt(pi / 2) / (6 * (W - 2) * (H - 2)) * sum(|Y * N|)
   
   Assumptions & Limitations:
   - ASSUMPTION: Noise is primarily additive and high-frequency.
   - LIMITATION: Extremely dense, high-frequency regular textures (like fine mesh or cloth) can
     partially activate this mask. Thus, this feature acts as an empirical "noise proxy" / high-frequency
     unstructured disturbance measure, rather than an absolute ground-truth sensor noise metric.

2. Dark Chroma Variance:
   Computes the variance of chrominance channels (U and V) specifically in low-light pixels (Y < 40.0).
   Digital image sensors suffer severe thermal/shot noise in shadow regions, appearing as chrominance
   blotches (chroma noise). Lossy compression often turns this into ugly color artifacts.
"""

import numpy as np
from scipy import signal
from typing import Dict
from ..color.color_space import get_luminance, rgb_to_yuv


def extract_noise_features(rgb_img: np.ndarray) -> Dict[str, float]:
    """
    Extracts empirical noise proxies from luminance and chrominance:
    - noise_estimate: Immerkaer pseudo-Laplacian noise proxy
    - dark_chroma_variance: Average chroma variance in low-luminance pixels (Y < 40)
    """
    Y = get_luminance(rgb_img)
    H, W = Y.shape
    if H < 3 or W < 3:
        return {"noise_estimate": 0.0, "dark_chroma_variance": 0.0}

    # Immerkaer 3x3 pseudo-Laplacian mask
    mask = np.array([
        [ 1.0, -2.0,  1.0],
        [-2.0,  4.0, -2.0],
        [ 1.0, -2.0,  1.0]
    ], dtype=np.float32)

    conv = signal.convolve2d(Y, mask, mode="valid")
    sigma_n = float(np.sum(np.abs(conv)) * np.sqrt(np.pi / 2.0) / (6.0 * (W - 2) * (H - 2)))

    # Dark chroma noise
    yuv = rgb_to_yuv(rgb_img)
    dark_mask = yuv[..., 0] < 40.0
    if np.count_nonzero(dark_mask) > 100:
        dark_u_var = float(np.var(yuv[..., 1][dark_mask]))
        dark_v_var = float(np.var(yuv[..., 2][dark_mask]))
        dark_chroma_var = float((dark_u_var + dark_v_var) / 2.0)
    else:
        dark_chroma_var = 0.0

    return {
        "noise_estimate": sigma_n,
        "dark_chroma_variance": dark_chroma_var
    }

