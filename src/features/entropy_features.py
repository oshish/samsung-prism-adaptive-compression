import numpy as np
from scipy import stats
from typing import Dict
from ..preprocessing.color_space import get_luminance, split_yuv_channels, rgb_to_yuv

def extract_entropy_features(rgb_img: np.ndarray) -> Dict[str, float]:
    """
    Calculates Shannon entropy and colorfulness metrics.
    """
    Y = get_luminance(rgb_img)
    
    # Shannon entropy of luminance (bins = 256)
    hist, _ = np.histogram(Y.ravel(), bins=256, range=(0, 256), density=True)
    hist = hist[hist > 0]
    shannon_entropy_y = float(-np.sum(hist * np.log2(hist))) if hist.size > 0 else 0.0
    
    # Color entropy across RGB channels
    color_entropies = []
    for c in range(3):
        ch = rgb_img[..., c]
        ch_hist, _ = np.histogram(ch.ravel(), bins=256, range=(0, 256), density=True)
        ch_hist = ch_hist[ch_hist > 0]
        if ch_hist.size > 0:
            color_entropies.append(-np.sum(ch_hist * np.log2(ch_hist)))
        else:
            color_entropies.append(0.0)
    color_entropy_mean = float(np.mean(color_entropies))
    
    # Hasler & Süsstrunk Colorfulness Metric
    R = rgb_img[..., 0].astype(np.float32)
    G = rgb_img[..., 1].astype(np.float32)
    B = rgb_img[..., 2].astype(np.float32)
    rg = R - G
    yb = 0.5 * (R + G) - B
    std_rg, mean_rg = float(np.std(rg)), float(np.mean(rg))
    std_yb, mean_yb = float(np.std(yb)), float(np.mean(yb))
    std_rgyb = np.sqrt(std_rg**2 + std_yb**2)
    mean_rgyb = np.sqrt(mean_rg**2 + mean_yb**2)
    colorfulness = float(std_rgyb + 0.3 * mean_rgyb)
    
    # Chroma standard deviations in YUV
    yuv = rgb_to_yuv(rgb_img)
    _, U, V = split_yuv_channels(yuv)
    chroma_std_u = float(np.std(U))
    chroma_std_v = float(np.std(V))

    return {
        "shannon_entropy_y": shannon_entropy_y,
        "color_entropy_mean": color_entropy_mean,
        "colorfulness": colorfulness,
        "chroma_std_u": chroma_std_u,
        "chroma_std_v": chroma_std_v
    }
