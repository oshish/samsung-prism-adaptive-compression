import numpy as np
from typing import Tuple

# ITU-R BT.601 transformation matrix coefficients
# Y  = 0.299*R + 0.587*G + 0.114*B
# Cb = -0.168736*R - 0.331264*G + 0.5*B + 128
# Cr = 0.5*R - 0.418688*G - 0.081312*B + 128
BT601_RGB_TO_YUV = np.array([
    [0.299000,  0.587000,  0.114000],
    [-0.168736, -0.331264,  0.500000],
    [0.500000, -0.418688, -0.081312]
], dtype=np.float32)

BT601_YUV_TO_RGB = np.linalg.inv(BT601_RGB_TO_YUV)

# ITU-R BT.709 transformation matrix coefficients
BT709_RGB_TO_YUV = np.array([
    [0.212600,  0.715200,  0.072200],
    [-0.114572, -0.385428,  0.500000],
    [0.500000, -0.454153, -0.045847]
], dtype=np.float32)

BT709_YUV_TO_RGB = np.linalg.inv(BT709_RGB_TO_YUV)

def rgb_to_yuv(rgb_img: np.ndarray, standard: str = "BT601") -> np.ndarray:
    """
    Converts an RGB image [0, 255] uint8 to YUV (YCbCr) float32.
    Y in [0, 255], U in [0, 255], V in [0, 255] with chroma offset 128.
    """
    matrix = BT601_RGB_TO_YUV if standard.upper() == "BT601" else BT709_RGB_TO_YUV
    rgb_f = rgb_img.astype(np.float32)
    # Shape (H, W, 3) dot (3, 3).T
    yuv = np.dot(rgb_f, matrix.T)
    # Add 128 offset to chroma channels
    yuv[..., 1] += 128.0
    yuv[..., 2] += 128.0
    return np.clip(yuv, 0.0, 255.0)

def yuv_to_rgb(yuv_img: np.ndarray, standard: str = "BT601") -> np.ndarray:
    """
    Converts YUV float32 [0, 255] back to RGB uint8 [0, 255].
    """
    inv_matrix = BT601_YUV_TO_RGB if standard.upper() == "BT601" else BT709_YUV_TO_RGB
    yuv_centered = yuv_img.astype(np.float32).copy()
    yuv_centered[..., 1] -= 128.0
    yuv_centered[..., 2] -= 128.0
    rgb = np.dot(yuv_centered, inv_matrix.T)
    return np.clip(np.round(rgb), 0, 255).astype(np.uint8)

def get_luminance(rgb_img: np.ndarray, standard: str = "BT601") -> np.ndarray:
    """
    Extracts the 2D luminance (Y) map as float32 in range [0, 255].
    """
    if rgb_img.ndim == 2:
        return rgb_img.astype(np.float32)
    if standard.upper() == "BT601":
        weights = np.array([0.299, 0.587, 0.114], dtype=np.float32)
    else:
        weights = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    return np.tensordot(rgb_img.astype(np.float32), weights, axes=([2], [0]))

def split_yuv_channels(yuv_img: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Splits YUV array into individual 2D (Y, U, V) planes.
    """
    return yuv_img[..., 0], yuv_img[..., 1], yuv_img[..., 2]
