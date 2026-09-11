"""
src/features/color.py
Extracts channel statistics from RGB and YUV color representations and Hasler-Süsstrunk colorfulness.

Relevance to Compression:
1. RGB Distribution:
   Captures individual color plane energies. Certain channels (e.g. Blue) often contain higher sensor
   noise and lower visual contrast.
2. YUV Chrominance Statistics (U & V):
   U (Cb) and V (Cr) represent color differences. When std_u and std_v are low, chroma components
   are nearly constant and compress to almost zero bits under transform coding.
3. Hasler & Süsstrunk Colorfulness Metric (2003):
   Quantifies perceived color saturation and chromatic complexity:
       rg = R - G
       yb = 0.5 * (R + G) - B
       M = sqrt(std_rg^2 + std_yb^2) + 0.3 * sqrt(mean_rg^2 + mean_yb^2)
"""

import numpy as np
from typing import Dict
from ..color.color_space import rgb_to_yuv, split_yuv_channels


def extract_color_features(rgb_img: np.ndarray) -> Dict[str, float]:
    """
    Extracts RGB channel moments, YUV chrominance moments, and Hasler-Süsstrunk colorfulness:
    - mean_r, mean_g, mean_b: Mean intensity per channel [0, 255]
    - std_r, std_g, std_b: Standard deviation per channel
    - mean_u, mean_v: Mean chrominance (centered around 128)
    - std_u, std_v: Standard deviation of chrominance
    - colorfulness: Hasler-Süsstrunk chromatic vibrancy index
    """
    R = rgb_img[..., 0].astype(np.float32)
    G = rgb_img[..., 1].astype(np.float32)
    B = rgb_img[..., 2].astype(np.float32)

    mean_r, std_r = float(np.mean(R)), float(np.std(R))
    mean_g, std_g = float(np.mean(G)), float(np.std(G))
    mean_b, std_b = float(np.mean(B)), float(np.std(B))

    # YUV chrominance channels
    yuv = rgb_to_yuv(rgb_img)
    _, U, V = split_yuv_channels(yuv)
    mean_u, std_u = float(np.mean(U)), float(np.std(U))
    mean_v, std_v = float(np.mean(V)), float(np.std(V))

    # Hasler & Süsstrunk Colorfulness Metric
    rg = R - G
    yb = 0.5 * (R + G) - B
    std_rg, mean_rg = float(np.std(rg)), float(np.mean(rg))
    std_yb, mean_yb = float(np.std(yb)), float(np.mean(yb))
    std_rgyb = float(np.sqrt(std_rg**2 + std_yb**2))
    mean_rgyb = float(np.sqrt(mean_rg**2 + mean_yb**2))
    colorfulness = float(std_rgyb + 0.3 * mean_rgyb)

    return {
        "mean_r": mean_r,
        "mean_g": mean_g,
        "mean_b": mean_b,
        "std_r": std_r,
        "std_g": std_g,
        "std_b": std_b,
        "mean_u": mean_u,
        "mean_v": mean_v,
        "std_u": std_u,
        "std_v": std_v,
        "colorfulness": colorfulness
    }

