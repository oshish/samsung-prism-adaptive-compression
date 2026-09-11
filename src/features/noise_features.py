import numpy as np
from scipy import signal
from typing import Dict
from ..preprocessing.color_space import get_luminance, rgb_to_yuv

def extract_noise_features(rgb_img: np.ndarray) -> Dict[str, float]:
    """
    Estimates additive Gaussian noise using Immerkaer's fast Laplacian mask method.
    Also estimates chroma noise in dark regions.
    """
    Y = get_luminance(rgb_img)
    H, W = Y.shape
    if H < 3 or W < 3:
        return {"noise_estimate": 0.0, "dark_chroma_variance": 0.0}
    
    # Immerkaer Laplacian noise estimation mask
    # N = [ 1 -2  1 ]
    #     [-2  4 -2 ]
    #     [ 1 -2  1 ]
    mask = np.array([
        [ 1, -2,  1],
        [-2,  4, -2],
        [ 1, -2,  1]
    ], dtype=np.float32)
    
    conv = signal.convolve2d(Y, mask, mode="valid")
    # sigma_n = sqrt(pi / 2) / (6 * (W-2) * (H-2)) * sum(|conv|)
    sigma_n = float(np.sum(np.abs(conv)) * np.sqrt(np.pi / 2.0) / (6.0 * (W - 2) * (H - 2)))
    
    # Chroma noise in dark regions
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
