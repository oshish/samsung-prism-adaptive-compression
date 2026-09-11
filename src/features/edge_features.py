import numpy as np
from scipy import ndimage
from typing import Dict
from ..preprocessing.color_space import get_luminance

def extract_edge_features(
    rgb_img: np.ndarray,
    sobel_threshold: float = 30.0
) -> Dict[str, float]:
    """
    Extracts structural edge features using Sobel and Laplacian operators.
    """
    Y = get_luminance(rgb_img)
    
    # Sobel gradient in x and y
    sobel_x = ndimage.sobel(Y, axis=1, mode="reflect")
    sobel_y = ndimage.sobel(Y, axis=0, mode="reflect")
    gradient_magnitude = np.hypot(sobel_x, sobel_y)
    
    mean_gradient = float(np.mean(gradient_magnitude))
    max_gradient = float(np.max(gradient_magnitude)) if gradient_magnitude.size > 0 else 0.0
    
    # Edge density: fraction of pixels exceeding edge threshold
    edge_pixels = np.count_nonzero(gradient_magnitude > sobel_threshold)
    edge_density = float(edge_pixels / float(gradient_magnitude.size))
    
    # Laplacian variance (standard measure of focus/sharpness/high-frequency texture)
    laplacian = ndimage.laplace(Y, mode="reflect")
    laplacian_var = float(np.var(laplacian))
    
    return {
        "sobel_mean_magnitude": mean_gradient,
        "sobel_max_magnitude": max_gradient,
        "sobel_edge_density": edge_density,
        "laplacian_variance": laplacian_var
    }
