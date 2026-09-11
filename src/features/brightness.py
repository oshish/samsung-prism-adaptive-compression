"""
src/features/brightness.py
Extracts first- and higher-order luminance and brightness distribution statistics.

Luminance (Y) is derived via ITU-R BT.601 standard:
Y = 0.299*R + 0.587*G + 0.114*B

Dark/Bright Threshold Justifications:
- dark_pixel_cutoff = 40.0 (~15.7% intensity): conventional threshold for shadow / underexposure
  regions where sensor noise predominates and lossy quantizers tend to produce blocking/contouring.
- bright_pixel_cutoff = 215.0 (~84.3% intensity): highlight region near saturation where clipping
  and high-frequency ringing are most visible to human observers.
"""

import numpy as np
from typing import Dict
from ..color.color_space import get_luminance


def extract_brightness_features(
    rgb_img: np.ndarray,
    dark_cutoff: float = 40.0,
    bright_cutoff: float = 215.0
) -> Dict[str, float]:
    """
    Extracts fundamental luminance distribution features from an RGB image.
    
    Returns:
        mean_luminance: Average brightness across frame [0, 255]
        std_luminance: Global brightness dispersion [0, 128]
        min_luminance: Minimum pixel intensity [0, 255]
        max_luminance: Maximum pixel intensity [0, 255]
        median_luminance: 50th percentile brightness [0, 255]
        dark_pixel_ratio: Fraction of pixels with Y < dark_cutoff [0.0, 1.0]
        bright_pixel_ratio: Fraction of pixels with Y > bright_cutoff [0.0, 1.0]
    """
    Y = get_luminance(rgb_img)
    total_pixels = float(Y.size)
    if total_pixels == 0:
        return {}

    mean_y = float(np.mean(Y))
    std_y = float(np.std(Y))
    min_y = float(np.min(Y))
    max_y = float(np.max(Y))
    median_y = float(np.median(Y))
    
    dark_pixels = np.count_nonzero(Y < dark_cutoff)
    bright_pixels = np.count_nonzero(Y > bright_cutoff)
    
    dark_ratio = float(dark_pixels / total_pixels)
    bright_ratio = float(bright_pixels / total_pixels)

    return {
        "mean_luminance": mean_y,
        "std_luminance": std_y,
        "min_luminance": min_y,
        "max_luminance": max_y,
        "median_luminance": median_y,
        "dark_pixel_ratio": dark_ratio,
        "bright_pixel_ratio": bright_ratio
    }

