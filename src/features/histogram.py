"""
src/features/histogram.py
Extracts histogram distribution spread, percentiles, and Shannon information entropy.

Shannon Entropy Definition:
H(Y) = - sum_{i=0}^{255} p(i) * log2(p(i))
where p(i) is the empirical probability density of luminance intensity i in [0, 255].

Relevance to Compression:
Shannon entropy sets the theoretical minimum average bit rate (lossless compression limit)
for a memoryless source under optimal entropy coding (Huffman or Arithmetic coding).
A low entropy indicates a peaky, concentrated histogram (high compressibility), whereas
an entropy approaching 8.0 bits/pixel indicates an equiprobable distribution (maximum uncertainty/flat histogram).
"""

import numpy as np
from typing import Dict
from ..color.color_space import get_luminance


def extract_histogram_features(rgb_img: np.ndarray) -> Dict[str, float]:
    """
    Extracts histogram percentile spread and Shannon entropy:
    - p10_luminance: 10th percentile intensity
    - p90_luminance: 90th percentile intensity
    - iqr_luminance: Interquartile Range (75th percentile - 25th percentile)
    - shannon_entropy: Information entropy of luminance histogram in bits/pixel [0, 8]
    """
    Y = get_luminance(rgb_img)
    if Y.size == 0:
        return {}

    flat_y = Y.ravel()
    p10 = float(np.percentile(flat_y, 10))
    p90 = float(np.percentile(flat_y, 90))
    p25 = float(np.percentile(flat_y, 25))
    p75 = float(np.percentile(flat_y, 75))
    iqr = float(p75 - p25)
    
    # 256-bin discrete probability distribution
    counts, _ = np.histogram(flat_y, bins=256, range=(0, 256), density=False)
    total = float(flat_y.size)
    probs = counts / total
    non_zero_probs = probs[probs > 0]
    entropy = float(-np.sum(non_zero_probs * np.log2(non_zero_probs))) if non_zero_probs.size > 0 else 0.0

    return {
        "p10_luminance": p10,
        "p90_luminance": p90,
        "iqr_luminance": iqr,
        "shannon_entropy": entropy
    }

