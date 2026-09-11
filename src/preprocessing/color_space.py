"""
src/preprocessing/color_space.py
Compatibility proxy for src.color.color_space.
"""
from src.color.color_space import (
    BT601_RGB_TO_YUV,
    BT601_YUV_TO_RGB,
    BT709_RGB_TO_YUV,
    BT709_YUV_TO_RGB,
    rgb_to_yuv,
    yuv_to_rgb,
    get_luminance,
    split_yuv_channels,
)

__all__ = [
    "BT601_RGB_TO_YUV",
    "BT601_YUV_TO_RGB",
    "BT709_RGB_TO_YUV",
    "BT709_YUV_TO_RGB",
    "rgb_to_yuv",
    "yuv_to_rgb",
    "get_luminance",
    "split_yuv_channels",
]
