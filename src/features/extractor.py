import numpy as np
from typing import Dict, Any, Optional
from .brightness_features import extract_brightness_features
from .texture_features import extract_texture_features
from .edge_features import extract_edge_features
from .noise_features import extract_noise_features
from .entropy_features import extract_entropy_features
from ..preprocessing.image_loader import validate_image

def extract_features(rgb_img: np.ndarray, config: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
    """
    Unified feature extraction function.
    Extracts all pre-compression image features and returns a flat dictionary.
    
    GUARANTEE: Purely uncompressed image features. ZERO target leakage.
    """
    validate_image(rgb_img)
    
    cfg = config or {}
    dark_cutoff = cfg.get("dark_pixel_cutoff", 40.0)
    bright_cutoff = cfg.get("bright_pixel_cutoff", 215.0)
    patch_size = cfg.get("local_variance_patch_size", 8)
    sobel_thresh = cfg.get("sobel_edge_threshold", 30.0)
    
    features: Dict[str, float] = {}
    
    # 1. Brightness & Luminance
    features.update(extract_brightness_features(
        rgb_img,
        dark_cutoff=dark_cutoff,
        bright_cutoff=bright_cutoff
    ))
    
    # 2. Texture & Spatial Variance
    features.update(extract_texture_features(
        rgb_img,
        patch_size=patch_size
    ))
    
    # 3. Edges & Sharpness
    features.update(extract_edge_features(
        rgb_img,
        sobel_threshold=sobel_thresh
    ))
    
    # 4. Noise Estimation
    features.update(extract_noise_features(rgb_img))
    
    # 5. Entropy & Color Complexity
    features.update(extract_entropy_features(rgb_img))
    
    # Ensure all values are finite and clean floats
    for k, v in features.items():
        if np.isnan(v) or np.isinf(v):
            features[k] = 0.0
        else:
            features[k] = float(v)
            
    return features
