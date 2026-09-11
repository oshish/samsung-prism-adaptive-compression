import numpy as np
from scipy import stats
from typing import Dict
from ..preprocessing.color_space import get_luminance

def extract_brightness_features(
    rgb_img: np.ndarray,
    dark_cutoff: float = 40.0,
    bright_cutoff: float = 215.0
) -> Dict[str, float]:
    """
    Extracts first- and higher-order luminance and brightness distribution statistics.
    """
    Y = get_luminance(rgb_img)
    total_pixels = float(Y.size)
    if total_pixels == 0:
        return {}

    mean_y = float(np.mean(Y))
    std_y = float(np.std(Y))
    
    # Skewness and kurtosis
    flat_y = Y.ravel()
    skew_y = float(stats.skew(flat_y)) if std_y > 1e-6 else 0.0
    kurt_y = float(stats.kurtosis(flat_y)) if std_y > 1e-6 else 0.0

    dark_pixels = np.count_nonzero(Y < dark_cutoff)
    bright_pixels = np.count_nonzero(Y > bright_cutoff)
    
    dark_ratio = float(dark_pixels / total_pixels)
    bright_ratio = float(bright_pixels / total_pixels)
    
    # RMS contrast
    rms_contrast = float(std_y / (mean_y + 1e-6))

    return {
        "mean_luminance": mean_y,
        "std_luminance": std_y,
        "skew_luminance": skew_y,
        "kurtosis_luminance": kurt_y,
        "dark_pixel_ratio": dark_ratio,
        "bright_pixel_ratio": bright_ratio,
        "rms_contrast": rms_contrast
    }
