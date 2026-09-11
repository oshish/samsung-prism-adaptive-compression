"""
src/features/edges.py
Extracts spatial edge features using Sobel gradient and Laplacian operators.

Edge Detection Method:
1. Horizontal (G_x) and vertical (G_y) gradients via 3x3 Sobel convolution kernels with reflect boundary conditions.
2. Gradient magnitude: |G| = sqrt(G_x^2 + G_y^2).
3. Edge density: fraction of pixels exceeding Sobel threshold (default: 30.0).
4. Focus / sharpness: variance of discrete 2D Laplacian operator.

Relevance to Compression:
Sharp edges correspond to significant high-frequency Fourier/DCT components.
Under lossy DCT quantization (e.g. JPEG), high-frequency coefficients are heavily attenuated,
causing Gibbs oscillations (ringing artifacts) and blurring along sharp object contours.
High edge density and high Laplacian variance suggest an image where lossy compression
artifacts will be acutely noticeable.
"""

import numpy as np
from scipy import ndimage
from typing import Dict
from ..color.color_space import get_luminance


def extract_edge_features(
    rgb_img: np.ndarray,
    sobel_threshold: float = 30.0
) -> Dict[str, float]:
    """
    Extracts structural edge and sharpness features from luminance:
    - sobel_edge_density: Proportion of pixels where gradient magnitude exceeds threshold [0.0, 1.0]
    - mean_edge_magnitude: Average gradient intensity across all pixels
    - std_edge_magnitude: Dispersion of gradient intensity
    - laplacian_variance: Variance of Laplacian response (focus / high-frequency energy)
    """
    Y = get_luminance(rgb_img)
    if Y.size == 0:
        return {}

    sobel_x = ndimage.sobel(Y, axis=1, mode="reflect")
    sobel_y = ndimage.sobel(Y, axis=0, mode="reflect")
    grad_mag = np.hypot(sobel_x, sobel_y)
    
    mean_mag = float(np.mean(grad_mag))
    std_mag = float(np.std(grad_mag))
    
    edge_pixels = np.count_nonzero(grad_mag > sobel_threshold)
    edge_density = float(edge_pixels / float(grad_mag.size))
    
    laplacian = ndimage.laplace(Y, mode="reflect")
    laplacian_var = float(np.var(laplacian))

    return {
        "sobel_edge_density": edge_density,
        "mean_edge_magnitude": mean_mag,
        "std_edge_magnitude": std_mag,
        "laplacian_variance": laplacian_var
    }

