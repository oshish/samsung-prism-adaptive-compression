"""
Modular feature extraction package.
"""
from .extractor import extract_features
from .brightness import extract_brightness_features
from .contrast import extract_contrast_features
from .histogram import extract_histogram_features
from .edges import extract_edge_features
from .texture import extract_texture_features
from .noise import extract_noise_features
from .color import extract_color_features

__all__ = [
    "extract_features",
    "extract_brightness_features",
    "extract_contrast_features",
    "extract_histogram_features",
    "extract_edge_features",
    "extract_texture_features",
    "extract_noise_features",
    "extract_color_features",
]
