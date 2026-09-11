"""
src/features/texture.py
Extracts spatial texture statistics: 8x8 non-overlapping block local variance and GLCM features.

Relevance to Compression:
The 8x8 patch size matches the native block transform partition used by JPEG and classic video codecs.
- local_variance_mean: Measures average intra-block activity. Smooth regions (sky, uniform walls) have
  near-zero block variance and compress efficiently. High-activity regions (foliage, fur, fabric) produce
  many non-zero AC coefficients.
- local_variance_std: Heterogeneity of texture across the frame (e.g. mixture of smooth sky and textured ground).
- glcm_contrast / glcm_homogeneity: Haralick Gray-Level Co-occurrence Matrix (GLCM) spatial relationships.
"""

import numpy as np
from typing import Dict
from skimage.feature import graycomatrix, graycoprops
from ..color.color_space import get_luminance


def extract_texture_features(
    rgb_img: np.ndarray,
    patch_size: int = 8
) -> Dict[str, float]:
    """
    Extracts spatial texture and block variation statistics:
    - local_variance_mean: Mean variance across 8x8 non-overlapping blocks
    - local_variance_std: Standard deviation of 8x8 block variances
    - glcm_contrast: Haralick contrast (intensity contrast between a pixel and its neighbor)
    - glcm_homogeneity: Haralick homogeneity (smoothness of gray level transitions)
    """
    Y = get_luminance(rgb_img)
    H, W = Y.shape
    if H < patch_size or W < patch_size:
        return {
            "local_variance_mean": 0.0,
            "local_variance_std": 0.0,
            "glcm_contrast": 0.0,
            "glcm_homogeneity": 0.0
        }
        
    # Pad to exact multiples of patch_size
    pad_h = (patch_size - (H % patch_size)) % patch_size
    pad_w = (patch_size - (W % patch_size)) % patch_size
    Y_padded = np.pad(Y, ((0, pad_h), (0, pad_w)), mode="reflect")
    
    blocks = Y_padded.reshape(
        Y_padded.shape[0] // patch_size, patch_size,
        Y_padded.shape[1] // patch_size, patch_size
    ).swapaxes(1, 2)
    
    block_vars = np.var(blocks, axis=(2, 3))
    mean_local_var = float(np.mean(block_vars))
    std_local_var = float(np.std(block_vars))
    
    # Fast GLCM on 16 quantized levels
    Y_quant = (Y / 16.0).astype(np.uint8)
    glcm = graycomatrix(
        Y_quant,
        distances=[1],
        angles=[0, np.pi/2],
        levels=16,
        symmetric=True,
        normed=True
    )
    
    contrast = float(np.mean(graycoprops(glcm, "contrast")))
    homogeneity = float(np.mean(graycoprops(glcm, "homogeneity")))

    return {
        "local_variance_mean": mean_local_var,
        "local_variance_std": std_local_var,
        "glcm_contrast": contrast,
        "glcm_homogeneity": homogeneity
    }

