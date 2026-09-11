import io
import os
import numpy as np
from PIL import Image
from typing import Tuple
from ..preprocessing.image_loader import validate_image

SUPPORTED_LOSSLESS = {"png", "webp_lossless"}
SUPPORTED_LOSSY = {"jpeg", "jpg", "webp_lossy"}

def compress_image(rgb_img: np.ndarray, codec: str = "png", quality: int = 75) -> bytes:
    """
    Compresses an RGB uint8 image into bytes using specified codec and quality.
    
    Args:
        rgb_img: np.ndarray of shape (H, W, 3), dtype uint8.
        codec: 'png', 'webp_lossless', 'jpeg', 'webp_lossy'.
        quality: Compression quality (1-100), used for lossy codecs.
        
    Returns:
        bytes of compressed image.
    """
    validate_image(rgb_img)
    pil_img = Image.fromarray(rgb_img, mode="RGB")
    buffer = io.BytesIO()
    
    codec_lower = codec.lower()
    if codec_lower == "png":
        pil_img.save(buffer, format="PNG", optimize=False)
    elif codec_lower == "webp_lossless":
        pil_img.save(buffer, format="WEBP", lossless=True, quality=100)
    elif codec_lower in ("jpeg", "jpg"):
        pil_img.save(buffer, format="JPEG", quality=int(np.clip(quality, 1, 100)), subsampling=0)
    elif codec_lower == "webp_lossy":
        pil_img.save(buffer, format="WEBP", lossless=False, quality=int(np.clip(quality, 1, 100)))
    else:
        raise ValueError(f"Unsupported codec: {codec}. Supported: {SUPPORTED_LOSSLESS | SUPPORTED_LOSSY}")
        
    return buffer.getvalue()

def decompress_image(compressed_bytes: bytes) -> np.ndarray:
    """
    Decompresses an in-memory byte buffer back to RGB uint8 numpy array.
    """
    buffer = io.BytesIO(compressed_bytes)
    with Image.open(buffer) as img:
        rgb_img = img.convert("RGB")
        return np.array(rgb_img, dtype=np.uint8)

def compress_to_file(rgb_img: np.ndarray, file_path: str, codec: str = "png", quality: int = 75) -> int:
    """
    Compresses image and saves to disk, returning the written file size in bytes.
    """
    compressed_bytes = compress_image(rgb_img, codec=codec, quality=quality)
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(compressed_bytes)
    return len(compressed_bytes)
