"""
src/features/contrast.py
Extracts dynamic range and contrast features from the luminance channel.

Contrast measures describe intensity variation and perceptual dynamic spread.
Low-contrast images contain narrow histograms (ideal for lossless Run-Length/Deflate or aggressive lossy DCT),
whereas high-contrast images contain sharp boundaries that suffer ringing artifacts under coarse quantization.
"""

import numpy as np
from typing import Dict
from ..color.color_space import get_luminance


def extract_contrast_features(rgb_img: np.ndarray) -> Dict[str, float]:
    """
    Extracts global contrast measures from luminance:
    - luminance_range: Absolute span between maximum and minimum pixel values [0, 255]
    - rms_contrast: Root-Mean-Square contrast, defined as standard deviation normalized by mean
    - michelson_contrast: (Y_max - Y_min) / (Y_max + Y_min + 1e-6)
    """
    Y = get_luminance(rgb_img)
    if Y.size == 0:
        return {}

    min_y = float(np.min(Y))
    max_y = float(np.max(Y))
    mean_y = float(np.mean(Y))
    std_y = float(np.std(Y))
    
    luminance_range = float(max_y - min_y)
    rms_contrast = float(std_y / (mean_y + 1e-6))
    michelson_contrast = float((max_y - min_y) / (max_y + min_y + 1e-6))

    return {
        "luminance_range": luminance_range,
        "rms_contrast": rms_contrast,
        "michelson_contrast": michelson_contrast
    }

