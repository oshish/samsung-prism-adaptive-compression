"""
src/features/extractor.py
Unified modular feature extraction interface.
Coordinates all individual feature extraction modules and returns a structured, flat dictionary.

GUARANTEE:
Purely pre-compression image properties.
ZERO target leakage (no compression ratios, no codec metrics, no ground-truth labels).
"""

import numpy as np
from typing import Dict, Any, Optional

from .brightness import extract_brightness_features
from .contrast import extract_contrast_features
from .histogram import extract_histogram_features
from .edges import extract_edge_features
from .texture import extract_texture_features
from .noise import extract_noise_features
from .color import extract_color_features
from ..preprocessing.image_loader import validate_image


def extract_features(
    rgb_img: np.ndarray,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, float]:
    """
    Extracts complete pre-compression feature set from a verified RGB image.
    
    Args:
        rgb_img: Numpy uint8 array of shape (H, W, 3).
        config: Optional parameter configuration dictionary.
        
    Returns:
        Flat dictionary of 32 numerical image features (4 structural + 28 visual characteristics).
    """
    validate_image(rgb_img)
    H, W, _ = rgb_img.shape
    
    cfg = config or {}
    dark_cutoff = cfg.get("dark_pixel_cutoff", 40.0)
    bright_cutoff = cfg.get("bright_pixel_cutoff", 215.0)
    sobel_thresh = cfg.get("sobel_edge_threshold", 30.0)
    patch_size = cfg.get("local_variance_patch_size", 8)
    
    features: Dict[str, float] = {}
    
    # 1. Structural / Metadata Features
    features["width"] = float(W)
    features["height"] = float(H)
    features["aspect_ratio"] = float(W / max(1, H))
    features["total_pixels"] = float(W * H)
    
    # 2. Brightness & Luminance
    features.update(extract_brightness_features(
        rgb_img,
        dark_cutoff=dark_cutoff,
        bright_cutoff=bright_cutoff
    ))
    
    # 3. Dynamic Range & Contrast
    features.update(extract_contrast_features(rgb_img))
    
    # 4. Histogram & Information Entropy
    features.update(extract_histogram_features(rgb_img))
    if "shannon_entropy" in features:
        features["shannon_entropy_y"] = features["shannon_entropy"]
    
    # 5. Edges & Sharpness
    features.update(extract_edge_features(
        rgb_img,
        sobel_threshold=sobel_thresh
    ))
    
    # 6. Texture & Spatial Variance
    features.update(extract_texture_features(
        rgb_img,
        patch_size=patch_size
    ))
    
    # 7. Noise Estimation Proxies
    features.update(extract_noise_features(rgb_img))
    
    # 8. RGB & YUV Color Characteristics
    features.update(extract_color_features(rgb_img))
    
    # Sanitize outputs: ensure deterministic, finite float values
    for k, v in features.items():
        val = float(v)
        if np.isnan(val) or np.isinf(val):
            features[k] = 0.0
        else:
            features[k] = val
            
    return features
