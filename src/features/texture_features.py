import numpy as np
from typing import Dict
from skimage.feature import graycomatrix, graycoprops
from ..preprocessing.color_space import get_luminance

def extract_texture_features(
    rgb_img: np.ndarray,
    patch_size: int = 8
) -> Dict[str, float]:
    """
    Extracts spatial texture statistics: local block variance and GLCM features.
    """
    Y = get_luminance(rgb_img)
    H, W = Y.shape
    
    # 1. Local patch variance
    # Pad if dimensions not divisible by patch_size
    pad_h = (patch_size - (H % patch_size)) % patch_size
    pad_w = (patch_size - (W % patch_size)) % patch_size
    Y_padded = np.pad(Y, ((0, pad_h), (0, pad_w)), mode="reflect")
    
    blocks = Y_padded.reshape(
        Y_padded.shape[0] // patch_size, patch_size,
        Y_padded.shape[1] // patch_size, patch_size
    ).swapaxes(1, 2)
    
    # Variance per block
    block_vars = np.var(blocks, axis=(2, 3))
    mean_local_var = float(np.mean(block_vars))
    std_local_var = float(np.std(block_vars))
    
    # 2. GLCM Haralick texture features
    # Quantize Y to 16 levels for fast GLCM computation
    Y_quant = (Y / 16.0).astype(np.uint8)
    glcm = graycomatrix(
        Y_quant,
        distances=[1, 2],
        angles=[0, np.pi/4, np.pi/2],
        levels=16,
        symmetric=True,
        normed=True
    )
    
    contrast = float(np.mean(graycoprops(glcm, "contrast")))
    dissimilarity = float(np.mean(graycoprops(glcm, "dissimilarity")))
    homogeneity = float(np.mean(graycoprops(glcm, "homogeneity")))
    energy = float(np.mean(graycoprops(glcm, "energy")))
    correlation = float(np.mean(graycoprops(glcm, "correlation")))
    
    return {
        "local_variance_mean": mean_local_var,
        "local_variance_std": std_local_var,
        "glcm_contrast": contrast,
        "glcm_dissimilarity": dissimilarity,
        "glcm_homogeneity": homogeneity,
        "glcm_energy": energy,
        "glcm_correlation": correlation if not np.isnan(correlation) else 0.0
    }
