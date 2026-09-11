import os
from typing import Dict, Any, Tuple
import numpy as np
from PIL import Image

def load_image(image_path: str) -> np.ndarray:
    """
    Loads an image from disk as a 24-bit RGB numpy array (uint8).
    
    Args:
        image_path: Path to image file.
    
    Returns:
        np.ndarray of shape (H, W, 3), dtype uint8.
    
    Raises:
        FileNotFoundError: If image file does not exist.
        ValueError: If file is corrupted or cannot be converted to RGB.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    try:
        with Image.open(image_path) as img:
            # Force conversion to 8-bit RGB
            rgb_img = img.convert("RGB")
            arr = np.array(rgb_img, dtype=np.uint8)
            validate_image(arr)
            return arr
    except Exception as e:
        raise ValueError(f"Failed to load/decode image {image_path}: {str(e)}") from e

def validate_image(arr: np.ndarray) -> None:
    """
    Validates array dimensions, channels, and data type.
    """
    if not isinstance(arr, np.ndarray):
        raise ValueError("Image must be a numpy ndarray")
    if arr.ndim != 3:
        raise ValueError(f"Image must have 3 dimensions (H, W, C), got ndim={arr.ndim}")
    if arr.shape[2] != 3:
        raise ValueError(f"Image must have 3 color channels, got shape={arr.shape}")
    if arr.shape[0] == 0 or arr.shape[1] == 0:
        raise ValueError(f"Image dimensions must be non-zero, got shape={arr.shape}")
    if arr.dtype != np.uint8:
        raise ValueError(f"Image dtype must be uint8, got {arr.dtype}")

def save_image(arr: np.ndarray, output_path: str, format: str = "PNG") -> None:
    """
    Saves a numpy RGB array to disk.
    """
    validate_image(arr)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img = Image.fromarray(arr, mode="RGB")
    img.save(output_path, format=format)

def get_image_metadata(arr: np.ndarray) -> Dict[str, Any]:
    """
    Returns image dimensions and raw uncompressed memory size.
    """
    validate_image(arr)
    height, width, channels = arr.shape
    raw_bytes = height * width * channels
    return {
        "height": int(height),
        "width": int(width),
        "channels": int(channels),
        "raw_bytes": int(raw_bytes),
        "aspect_ratio": float(width / max(1, height))
    }
